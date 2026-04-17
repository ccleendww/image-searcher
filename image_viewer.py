from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtGui import QPixmap, QWheelEvent, QPainter
from PySide6.QtCore import Qt

class InteractiveImageViewer(QGraphicsView):
    def __init__(self):
        super().__init__()
        # 1. 初始化场景与图元
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        # 2. 渲染优化：开启抗锯齿与平滑图片变换
        self.setRenderHint(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        
        # 3. 交互设置：开启鼠标拖拽平移，隐藏滚动条，设置暗黑背景
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.current_image_path = ""

    def load_image(self, image_path: str):
        """加载图像并自适应适应窗口大小"""
        self.current_image_path = image_path
        pixmap = QPixmap(image_path)
        
        if pixmap.isNull():
            return False

        self.pixmap_item.setPixmap(pixmap)
        # 将场景大小严格限定为图片真实物理大小
        self.scene.setSceneRect(self.pixmap_item.boundingRect())
        # 重置视图比例，使其适应当前窗口
        self.fit_to_window()
        return True

    def fit_to_window(self):
        """缩放视图以完整显示整个场景（图片）"""
        if not self.pixmap_item.pixmap().isNull():
            self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def wheelEvent(self, event: QWheelEvent):
        """重载滚轮事件，实现以鼠标指针为中心的无级缩放"""
        if self.pixmap_item.pixmap().isNull():
            return

        # 缩放步进系数
        zoom_in_factor = 1.15
        zoom_out_factor = 1.0 / zoom_in_factor

        # 核心：将缩放的锚点设置为鼠标当前位置
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # 判断滚轮方向 (angleDelta().y() > 0 向上滚，放大)
        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)

    def resizeEvent(self, event):
        """当软件主窗口缩放时，图片依然保持自适应居中"""
        super().resizeEvent(event)
        self.fit_to_window()

    def clear_view(self):
        """清空当前画板的内容"""
        self.current_image_path = ""
        # 传入一个空的 QPixmap 即可清空底层场景图元
        self.pixmap_item.setPixmap(QPixmap())