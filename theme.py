class Theme:
    DARK = "dark"
    LIGHT = "light"

    @staticmethod
    def get_main_window_stylesheet(theme_type):
        # ==========================================
        # 🌙 工业暗黑主题 (全局共鸣版)
        # 主题色: 赛博青 #00a8ff
        # 统一悬停色: 幽蓝碳灰 #1e2a30
        # ==========================================
        if theme_type == Theme.DARK:
            return """
            * {
                font-family: "Consolas", "Segoe UI", sans-serif;
                font-size: 13px;
                border-radius: 0px !important; 
                outline: none;
            }
            QMainWindow { background-color: #080808; }
            
            /* --- 列表与树状图 --- */
            QTreeView, QListWidget, QTextBrowser {
                background-color: #121212;
                color: #d4d4d4;
                border: 1px solid #2a2a2a;
                selection-background-color: #1c1c1c;
            }
            
            /* [核心修正] 列表悬停：注入低饱和度的青色，大幅提高可视度 */
            QTreeView::item:hover, QListWidget::item:hover {
                background-color: #1e2a30; 
                color: #ffffff;
            }
            
            /* 列表选中：保持高亮工业青色边界 */
            QTreeView::item:selected, QListWidget::item:selected {
                background-color: #1a1a1a;
                color: #ffffff;
                border-left: 2px solid #00a8ff; 
            }
            
            /* --- 输入框 --- */
            QLineEdit {
                background-color: #000000;
                color: #ffffff;
                border: 1px solid #333333;
                padding: 4px 8px;
            }
            QLineEdit:focus { border: 1px solid #00a8ff; }
            
            /* --- 按钮系统 --- */
            QPushButton {
                background-color: #1a1a1a;
                color: #cccccc;
                border: 1px solid #333333;
                padding: 4px 12px;
                font-weight: bold;
            }
            /* [核心修正] 按钮悬停：背景色与列表悬停完全一致，边框亮起暗青色形成呼应 */
            QPushButton:hover {
                background-color: #1e2a30;
                color: #ffffff;
                border: 1px solid #005c8a; 
            }
            QPushButton:pressed {
                background-color: #00a8ff;
                color: #000000;
                border: 1px solid #00a8ff;
            }
            QPushButton:disabled {
                background-color: #0f0f0f;
                color: #444444;
                border: 1px solid #1f1f1f;
            }
            
            /* --- 选项卡 (Tabs) --- */
            QTabWidget::pane { border-top: 1px solid #2a2a2a; }
            QTabBar::tab {
                background: #080808;
                color: #777777;
                padding: 6px 16px;
                border: 1px solid transparent;
                border-bottom: none;
            }
            /* [核心修正] 选项卡悬停：采用同一套幽蓝碳灰 */
            QTabBar::tab:hover {
                background: #1e2a30;
                color: #ffffff;
            }
            QTabBar::tab:selected {
                background: #121212;
                color: #00a8ff;
                border: 1px solid #2a2a2a;
                border-bottom: 1px solid #121212;
            }
            
            QSplitter::handle { background-color: #2a2a2a; margin: 0px; }
            QStatusBar {
                background-color: #000000;
                color: #666666;
                border-top: 1px solid #1a1a1a;
            }
            """
            
        # ==========================================
        # ☀️ 护眼工业灰白主题 (全局共鸣版)
        # 主题色: 工业蓝 #007ACC
        # 统一悬停色: 极浅蓝灰 #E6F0F9
        # ==========================================
        elif theme_type == Theme.LIGHT:
            return """
            * {
                font-family: "Consolas", "Segoe UI", sans-serif;
                font-size: 13px;
                border-radius: 0px !important; 
                outline: none;
            }
            
            QMainWindow { background-color: #F3F3F3; }

            /* --- 列表与树状图 --- */
            QTreeView, QListWidget, QTextBrowser {
                background-color: #FAFAFA;
                color: #333333; 
                border: 1px solid #DCDCDC;
                selection-background-color: #E8E8E8;
            }

            /* [核心修正] 列表悬停：注入极浅的工业蓝，一眼可见但不刺眼 */
            QTreeView::item:hover, QListWidget::item:hover {
                background-color: #E6F0F9;
                color: #000000;
            }

            QTreeView::item:selected, QListWidget::item:selected {
                background-color: #E0E0E0;
                color: #000000;
                border-left: 2px solid #007ACC; 
            }

            /* --- 输入框 --- */
            QLineEdit {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #CCCCCC;
                padding: 4px 8px;
            }
            QLineEdit:focus { border: 1px solid #007ACC; }
            
            /* --- 按钮系统 --- */
            QPushButton {
                background-color: #EBEBEB;
                color: #333333;
                border: 1px solid #CCCCCC;
                padding: 4px 12px;
                font-weight: bold;
            }
            /* [核心修正] 按钮悬停：背景色与列表完全一致，边框亮起浅蓝色 */
            QPushButton:hover {
                background-color: #E6F0F9;
                color: #000000;
                border: 1px solid #66B2FF;
            }
            QPushButton:pressed {
                background-color: #007ACC;
                color: #FFFFFF;
                border: 1px solid #007ACC;
            }
            QPushButton:disabled {
                background-color: #F9F9F9;
                color: #AAAAAA;
                border: 1px solid #E0E0E0;
            }

            /* --- 选项卡 (Tabs) --- */
            QTabWidget::pane { border-top: 1px solid #DCDCDC; }
            QTabBar::tab {
                background: #F3F3F3;
                color: #666666;
                padding: 6px 16px;
                border: 1px solid transparent;
                border-bottom: none;
            }
            /* [核心修正] 选项卡悬停：同样采用极浅蓝灰 */
            QTabBar::tab:hover {
                background: #E6F0F9;
                color: #007ACC;
            }
            QTabBar::tab:selected {
                background: #FAFAFA;
                color: #007ACC;
                border: 1px solid #DCDCDC;
                border-bottom: 1px solid #FAFAFA;
            }

            QSplitter::handle { background-color: #DCDCDC; margin: 0px; }
            QStatusBar {
                background-color: #EAEAEA;
                color: #555555;
                border-top: 1px solid #DCDCDC;
            }
            """
        return ""

    @staticmethod
    def get_image_viewer_stylesheet(theme_type):
        if theme_type == Theme.DARK:
            return """
            QGraphicsView {
                background-color: #0a0a0a;
                border: 1px solid #2a2a2a;
            }
            """
        elif theme_type == Theme.LIGHT:
            return """
            QGraphicsView {
                background-color: #E8E8E8;
                border: 1px solid #DCDCDC;
            }
            """
        return ""