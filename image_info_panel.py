"""
图片信息展示面板
显示图片的元数据信息：文件名、路径、大小、修改时间、分辨率等
"""

import os
from datetime import datetime

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class ImageInfoPanel(QWidget):
    """图片信息展示面板"""

    def __init__(self):
        super().__init__()
        self.current_image_path = ""
        self.setup_ui()

    def setup_ui(self):
        """初始化UI"""
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)

        # 标题
        title_label = QLabel("图片信息")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        title_label.setFont(title_font)
        self.layout.addWidget(title_label)

        # 分隔线
        separator = QLabel("─" * 40)
        self.layout.addWidget(separator)

        # 文件名
        self.filename_label = QLabel("文件名：-")
        self.layout.addWidget(self.filename_label)

        # 文件路径
        self.path_label = QLabel("路径：-")
        self.path_label.setWordWrap(True)
        self.layout.addWidget(self.path_label)

        # 文件大小
        self.size_label = QLabel("大小：-")
        self.layout.addWidget(self.size_label)

        # 修改时间
        self.date_label = QLabel("修改时间：-")
        self.date_label.setWordWrap(True)
        self.layout.addWidget(self.date_label)

        # 图片分辨率
        self.resolution_label = QLabel("分辨率：-")
        self.layout.addWidget(self.resolution_label)

        # 图片格式
        self.format_label = QLabel("格式：-")
        self.layout.addWidget(self.format_label)

        # 拉伸空间
        self.layout.addStretch()

        self.setLayout(self.layout)

    def update_info(self, image_path: str):
        """更新图片信息显示"""
        if not image_path or not os.path.exists(image_path):
            self.clear_info()
            return

        self.current_image_path = image_path

        try:
            # 文件名
            filename = os.path.basename(image_path)
            self.filename_label.setText(f"文件名：{filename}")

            # 完整路径
            self.path_label.setText(f"路径：{image_path}")

            # 文件大小
            file_size = os.path.getsize(image_path)
            size_str = self._format_size(file_size)
            self.size_label.setText(f"大小：{size_str}")

            # 修改时间
            mod_time = os.path.getmtime(image_path)
            mod_datetime = datetime.fromtimestamp(mod_time)
            date_str = mod_datetime.strftime("%Y-%m-%d %H:%M:%S")
            self.date_label.setText(f"修改时间：{date_str}")

            # 打开图片获取元数据
            try:
                with Image.open(image_path) as img:
                    # 分辨率
                    width, height = img.size
                    self.resolution_label.setText(f"分辨率：{width} × {height} 像素")

                    # 格式
                    image_format = img.format or "未知"
                    self.format_label.setText(f"格式：{image_format}")
            except Exception as e:
                # 如果无法读取图片元数据，显示错误
                self.resolution_label.setText("分辨率：无法读取")
                self.format_label.setText("格式：无法读取")

        except Exception as e:
            self.statusBar().showMessage(f"获取图片信息失败: {str(e)}")

    def clear_info(self):
        """清空信息显示"""
        self.current_image_path = ""
        self.filename_label.setText("文件名：-")
        self.path_label.setText("路径：-")
        self.size_label.setText("大小：-")
        self.date_label.setText("修改时间：-")
        self.resolution_label.setText("分辨率：-")
        self.format_label.setText("格式：-")

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """格式化字节大小为可读的字符串"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"
