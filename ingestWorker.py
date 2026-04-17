import traceback
from PySide6.QtCore import QThread, Signal

# 必须从你的核心逻辑模块中导入 ingest_images
from image_semantic_search import ingest_images

class IngestWorker(QThread):
    # 定义一个信号，用于在任务结束时向主线程传递状态（布尔值）和信息（字符串）
    finished_signal = Signal(bool, str)
    # 定义一个进度信号，用于在处理过程中更新进度
    progress_signal = Signal(int, int)  # current, total

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path

    def run(self):
        """
        这个函数将在独立的后台线程中执行。
        这里绝对不能包含任何 UI 相关的操作（如 QMessageBox 或 self.statusBar）。
        """
        try:
            # 执行极其耗时的底层运算，并传入进度回调
            ingest_images(self.folder_path, progress_callback=self.on_progress)
            # 运算成功，发射成功信号
            self.finished_signal.emit(True, "向量数据库构建成功！")
        except Exception as e:
            # 捕获崩溃日志并格式化，发射失败信号
            error_msg = f"底层执行失败: {str(e)}\n{traceback.format_exc()}"
            self.finished_signal.emit(False, error_msg)
    
    def on_progress(self, current, total):
        """进度回调函数"""
        self.progress_signal.emit(current, total)