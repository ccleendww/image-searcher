import sys
import winreg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QPushButton, QMessageBox, QHeaderView)

class StartupManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windows 启动项管理器")
        self.resize(700, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["状态", "名称", "路径", "作用域"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        self.btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("刷新")
        self.btn_delete = QPushButton("彻底删除选中项")
        self.btn_layout.addWidget(self.btn_refresh)
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.btn_delete)
        self.layout.addLayout(self.btn_layout)

        self.btn_refresh.clicked.connect(self.load_items)
        self.btn_delete.clicked.connect(self.delete_item)
        self.table.itemChanged.connect(self.on_item_changed)

        self.reg_paths = {
            True: r"Software\Microsoft\Windows\CurrentVersion\Run",
            False: r"Software\Microsoft\Windows\CurrentVersion\Run_Disabled"
        }

        self.load_items()

    def load_items(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)

        targets = [
            (winreg.HKEY_CURRENT_USER, "HKCU"),
            (winreg.HKEY_LOCAL_MACHINE, "HKLM")
        ]

        row = 0
        for hkey, scope in targets:
            for is_enabled, path in self.reg_paths.items():
                try:
                    key = winreg.OpenKey(hkey, path, 0, winreg.KEY_READ)
                    i = 0
                    while True:
                        try:
                            name, value, reg_type = winreg.EnumValue(key, i)
                            self.table.insertRow(row)

                            chk_item = QTableWidgetItem()
                            chk_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                            chk_item.setCheckState(Qt.Checked if is_enabled else Qt.Unchecked)
                            chk_item.setData(Qt.UserRole, (hkey, reg_type)) 
                            
                            self.table.setItem(row, 0, chk_item)
                            self.table.setItem(row, 1, QTableWidgetItem(name))
                            self.table.setItem(row, 2, QTableWidgetItem(value))
                            self.table.setItem(row, 3, QTableWidgetItem(scope))
                            row += 1
                            i += 1
                        except OSError:
                            break
                    winreg.CloseKey(key)
                except FileNotFoundError:
                    pass
                except PermissionError:
                    pass
        self.table.blockSignals(False)

    def on_item_changed(self, item):
        if item.column() != 0:
            return

        row = item.row()
        new_state = (item.checkState() == Qt.Checked)
        name = self.table.item(row, 1).text()
        value = self.table.item(row, 2).text()
        hkey, reg_type = item.data(Qt.UserRole)

        source_path = self.reg_paths[not new_state]
        target_path = self.reg_paths[new_state]

        try:
            target_key = winreg.CreateKey(hkey, target_path)
            winreg.SetValueEx(target_key, name, 0, reg_type, value)
            winreg.CloseKey(target_key)

            source_key = winreg.OpenKey(hkey, source_path, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(source_key, name)
            winreg.CloseKey(source_key)

        except PermissionError:
            self.table.blockSignals(True)
            item.setCheckState(Qt.Unchecked if new_state else Qt.Checked)
            self.table.blockSignals(False)
            QMessageBox.critical(self, "权限被拒绝", "修改 HKLM 启动项需要管理员权限。")
        except Exception as e:
            self.table.blockSignals(True)
            item.setCheckState(Qt.Unchecked if new_state else Qt.Checked)
            self.table.blockSignals(False)
            QMessageBox.critical(self, "错误", str(e))

    def delete_item(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            return

        chk_item = self.table.item(current_row, 0)
        is_enabled = (chk_item.checkState() == Qt.Checked)
        name = self.table.item(current_row, 1).text()
        hkey, _ = chk_item.data(Qt.UserRole)
        path = self.reg_paths[is_enabled]

        try:
            key = winreg.OpenKey(hkey, path, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, name)
            winreg.CloseKey(key)
            self.load_items()
        except PermissionError:
            QMessageBox.critical(self, "权限被拒绝", "需要管理员权限。")
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StartupManager()
    window.show()
    sys.exit(app.exec())