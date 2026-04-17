import os
import sys

import qtawesome as qta
from PySide6.QtCore import QDir, QSize, Qt
from PySide6.QtGui import QAction, QIcon, QPalette, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFileSystemModel,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from image_semantic_search import remove_index, search_image
from image_viewer import InteractiveImageViewer
from image_info_panel import ImageInfoPanel
from ingestWorker import IngestWorker
from theme import Theme


class ImageBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" Image Search")
        self.resize(1200, 800)
        # 设置窗口图标
        self.setWindowIcon(QIcon("app.ico"))
        self.current_image_path = ""
        self.current_folder_path = ""
        # 检测系统主题并初始化
        self.current_theme = self.detect_system_theme()
        # 初始化进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar)
        self.setup_ui()
        self.setup_menu()
        self.apply_theme()

    def detect_system_theme(self):
        """检测系统主题，返回Theme.LIGHT或Theme.DARK"""
        try:
            # 尝试使用Qt 6.5+的colorScheme()方法
            app = QApplication.instance()
            if hasattr(app.styleHints(), 'colorScheme'):
                from PySide6.QtCore import Qt
                color_scheme = app.styleHints().colorScheme()
                if color_scheme == Qt.ColorScheme.Dark:
                    return Theme.DARK
                else:
                    return Theme.LIGHT
        except:
            pass

        # 回退方法：检查调色板
        try:
            palette = QApplication.palette()
            # 检查窗口背景色的亮度
            window_color = palette.color(QPalette.ColorRole.Window)
            # 计算亮度 (使用相对亮度公式)
            brightness = (0.299 * window_color.red() +
                         0.587 * window_color.green() +
                         0.114 * window_color.blue()) / 255

            # 如果亮度低于0.5，认为是暗色主题
            if brightness < 0.5:
                return Theme.DARK
            else:
                return Theme.LIGHT
        except:
            # 如果检测失败，默认使用亮色主题
            return Theme.LIGHT

    def setup_ui(self):
        # 使用 QSplitter 实现左右面板的可拖拽分割
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.splitter)

        # ==========================================
        # 左侧：选项卡面板 (文件夹树视图 + 搜索结果)
        # ==========================================
        self.left_tabs = QTabWidget()

        # --- Tab 1: 层叠文件夹树视图 ---
        self.file_model = QFileSystemModel()
        self.file_model.setFilter(
            QDir.Filter.NoDotAndDotDot | QDir.Filter.AllDirs | QDir.Filter.Files
        )
        self.file_model.setNameFilters(["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.webp"])
        self.file_model.setNameFilterDisables(False)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)
        for i in range(1, 4):
            self.tree_view.hideColumn(i)
        self.tree_view.clicked.connect(self.on_tree_clicked)

        # --- Tab 2: 搜索结果扁平列表 ---
        self.search_results_list = QListWidget()
        self.search_results_list.itemClicked.connect(self.on_search_result_clicked)

        # 将树视图和列表加入选项卡
        self.left_tabs.addTab(self.tree_view, "本地目录")
        self.left_tabs.addTab(self.search_results_list, "检索结果")

        # ==========================================
        # 右侧：搜索栏 + 图片显示区域
        # ==========================================
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(5)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("")
        self.search_input.setMaximumHeight(35)
        self.search_input.returnPressed.connect(self.on_search)

        self.search_button = QPushButton("搜索")
        self.search_button.setMaximumWidth(80)
        self.search_button.setMaximumHeight(35)

        self.ocr_button = QPushButton("构建索引")
        self.ocr_button.setMaximumWidth(80)
        self.ocr_button.setMaximumHeight(35)
        self.remove_db_button = QPushButton("清除索引")
        self.remove_db_button.setMaximumWidth(80)
        self.remove_db_button.setMaximumHeight(35)

        # 实例化一个纯图标按钮
        self.theme_button = QPushButton()
        # 根据当前主题设置初始图标
        if self.current_theme == Theme.DARK:
            # 暗色主题时显示太阳图标（可以切换到亮色）
            self.theme_button.setIcon(qta.icon("fa5s.sun", color="#e0e0e0"))
        else:
            # 亮色主题时显示月亮图标（可以切换到暗色）
            self.theme_button.setIcon(qta.icon("fa5s.moon", color="#555555"))
        self.theme_button.setIconSize(QSize(20, 20))
        # 设置为等宽高的正方形，符合极简审美
        self.theme_button.setFixedSize(35, 35)
        # 增加悬停提示替代原有文字
        self.theme_button.setToolTip("切换主题")

        self.search_button.clicked.connect(self.on_search)
        self.ocr_button.clicked.connect(self.ingest_images_dialog)
        self.remove_db_button.clicked.connect(self.clear_db)
        self.theme_button.clicked.connect(self.toggle_theme)

        # search_layout.addWidget(QLabel("搜索:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.ocr_button)
        search_layout.addWidget(self.remove_db_button)
        search_layout.addStretch()
        search_layout.addWidget(self.theme_button)

        # 图片显示组件
        self.image_viewer = InteractiveImageViewer()

        # 图片信息面板
        self.image_info_panel = ImageInfoPanel()
        self.image_info_panel.setMaximumHeight(250)

        right_layout.addLayout(search_layout)
        right_layout.addWidget(self.image_viewer, 1)
        right_layout.addWidget(self.image_info_panel)

        # 组合左右面板 (用 self.left_tabs 替换原来的 self.tree_view)
        self.splitter.addWidget(self.left_tabs)
        self.splitter.addWidget(right_widget)
        self.splitter.setSizes([300, 900])

    def setup_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Open Folder", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_action)

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择工作目录")
        if not folder_path:
            return

        self.current_folder_path = folder_path
        self.statusBar().showMessage(f"{folder_path}")

        self.file_model.setRootPath(folder_path)
        self.tree_view.setRootIndex(self.file_model.index(folder_path))

        # 严谨的交互逻辑：打开新文件夹时清空旧画板
        self.image_viewer.clear_view()
        self.image_info_panel.clear_info()

    def on_tree_clicked(self, index):
        """处理左侧目录树的点击事件"""
        if not self.file_model.isDir(index):
            file_path = self.file_model.filePath(index)
            self.current_image_path = file_path
            self.update_image_display()

    def on_search_result_clicked(self, item):
        """处理左侧检索结果列表的点击事件"""
        # 提取绑定在底层的绝对路径
        file_path = item.data(Qt.ItemDataRole.UserRole)

        if file_path and os.path.exists(file_path):
            self.current_image_path = file_path
            self.update_image_display()
        else:
            self.statusBar().showMessage("错误：该文件已被移动或删除")

    def update_image_display(self):
        """调用封装好的查看器加载图像"""
        if not self.current_image_path:
            return

        success = self.image_viewer.load_image(self.current_image_path)
        if not success:
            self.statusBar().showMessage("无法解析该图像文件")
        else:
            # 更新图片信息面板
            self.image_info_panel.update_info(self.current_image_path)
        return

    def on_search(self):
        """处理搜索操作并渲染结果列表"""
        query = self.search_input.text().strip()
        if not query:
            return

        self.statusBar().showMessage("正在检索...")

        # 接收底层引擎返回的结果列表
        results = search_image(query)

        # 1. 清空旧列表
        self.search_results_list.clear()

        if not results:
            self.statusBar().showMessage("未找到相关图像")
            return

        # 2. 填充新列表
        for item in results:
            distance = item["distance"]
            image_path = item["image_path"]
            filename = os.path.basename(image_path)

            # 排版：文件名在上，距离在下
            display_text = f"{filename}\n[距离: {distance:.4f}]"
            list_item = QListWidgetItem(display_text)

            # 绑定绝对路径为隐藏数据
            list_item.setData(Qt.ItemDataRole.UserRole, image_path)
            self.search_results_list.addItem(list_item)

        # 3. 自动跳转到“检索结果”选项卡
        self.left_tabs.setCurrentIndex(1)
        self.statusBar().showMessage(
            f"检索完毕，共找到 {len(results)} 张高度匹配的图像"
        )

    def ingest_images_dialog(self):
        """触发后台 OCR 建造向量数据库"""
        if not getattr(self, "current_folder_path", ""):
            QMessageBox.warning(
                self,
                "操作错误",
                "请先通过菜单栏 File -> Open Folder 选择一个图片文件夹！",
            )
            return

        self.statusBar().showMessage(
            f"正在后台对 {self.current_folder_path} 进行计算，您可以继续浏览其他图片..."
        )
        self.ocr_button.setEnabled(False)
        self.remove_db_button.setEnabled(False)

        # 显示进度条
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

        self.ingest_thread = IngestWorker(self.current_folder_path)
        # 连接进度信号
        self.ingest_thread.progress_signal.connect(self.on_progress_update)
        self.ingest_thread.finished_signal.connect(self.on_ingest_finished)
        self.ingest_thread.start()

    def on_progress_update(self, current, total):
        """处理进度更新"""
        if total > 0:
            progress_percent = int((current / total) * 100)
            self.progress_bar.setValue(progress_percent)
            self.progress_bar.setFormat(f"{current}/{total} 图片")
            self.statusBar().showMessage(f"处理中... [{current}/{total}]")

    def on_ingest_finished(self, success: bool, message: str):
        """接收后台线程信号的回调函数"""
        self.ocr_button.setEnabled(True)
        self.remove_db_button.setEnabled(True)

        # 隐藏进度条
        self.progress_bar.setVisible(False)

        if success:
            self.statusBar().showMessage("后台索引构建完成")
            QMessageBox.information(self, "完成", message)
        else:
            self.statusBar().showMessage("后台索引构建发生致命错误")
            QMessageBox.critical(self, "严重错误", message)

        self.ingest_thread.deleteLater()

    def clear_db(self):
        """清除向量数据库索引"""
        confirm = QMessageBox.warning(
            self,
            "清除索引确认",
            "确定要清除向量数据库索引吗？此操作不可恢复。",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        )
        if confirm != QMessageBox.StandardButton.Ok:
            return
        remove_index()

    def apply_theme(self):
        """应用当前主题到所有组件"""
        # 应用主窗口样式表
        self.setStyleSheet(Theme.get_main_window_stylesheet(self.current_theme))
        # 应用图片查看器样式表
        self.image_viewer.setStyleSheet(
            Theme.get_image_viewer_stylesheet(self.current_theme)
        )
        # 应用信息面板样式表
        self.image_info_panel.setStyleSheet(
            Theme.get_image_viewer_stylesheet(self.current_theme)
        )

        # 为进度条应用主题样式（绿色进度条）
        # 工业风极细进度条
        progress_stylesheet = """
            QProgressBar {
                border: 1px solid #333333;
                border-radius: 0px;
                background-color: #000000;
                color: #ffffff;
                text-align: center;
                height: 18px;
            }
            QProgressBar::chunk {
                background-color: #00a8ff;
                width: 1px; /* 极客风：取消平滑填充，使用点阵或单像素递进感 */
            }
        """
        self.progress_bar.setStyleSheet(progress_stylesheet)
        self.progress_bar.setStyleSheet(progress_stylesheet)

    def toggle_theme(self):
        """切换主题"""
        if self.current_theme == Theme.DARK:
            self.current_theme = Theme.LIGHT
            # 切换回亮色主题时，图标变成月亮（提示可切换暗色），颜色调暗
            self.theme_button.setIcon(qta.icon("fa5s.moon", color="#555555"))
        else:
            self.current_theme = Theme.DARK
            # 切换到暗黑主题时，图标变成太阳，颜色调为明亮的反色
            self.theme_button.setIcon(qta.icon("fa5s.sun", color="#e0e0e0"))

        self.apply_theme()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    window = ImageBrowser()
    window.show()
    sys.exit(app.exec())
