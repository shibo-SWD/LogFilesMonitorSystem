import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QLabel, 
    QTextEdit, QStatusBar, QAction, QMenuBar
)
from PyQt5.QtCore import Qt
from server.server_backend import FileServer
from ui.server_gui import ServerGUI

def main():
    app = QApplication(sys.argv)
    gui = ServerGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()