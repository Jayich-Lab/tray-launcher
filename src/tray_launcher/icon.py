from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QSystemTrayIcon, qApp, QApplication, QMessageBox, QMainWindow, QMenu, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon
import sys

from launcher_core import launcher_core

def main():
        app = QApplication(sys.argv)
        lc = QSystemTrayIcon()
        lc.setIcon(QIcon(r"C:\Users\scientist\code\jam\tray_launcher\tray_icon.png"))
        lc.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()