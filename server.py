# server_gui.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QLabel, 
    QTextEdit, QStatusBar, QAction, QMenuBar
)
from PyQt5.QtCore import Qt
from server_backend import FileServer

class ServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.file_server = None

    def initUI(self):
        """初始化UI组件"""
        self.setWindowTitle('文件监控服务端')
        self.resize(600, 400)  # 设置窗口大小

        # 中央Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # 状态显示
        self.status_label = QLabel('服务器未启动')
        layout.addWidget(self.status_label)

        # 日志显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # 启动和关闭按钮
        self.start_button = QPushButton('启动服务器')
        self.start_button.clicked.connect(self.start_server)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton('关闭服务器')
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_server)
        layout.addWidget(self.stop_button)

        central_widget.setLayout(layout)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        file_menu.addAction(about_action)

        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 主题选择菜单
        theme_menu = menubar.addMenu('主题')
        light_theme_action = QAction('明亮主题', self)
        light_theme_action.triggered.connect(self.set_light_theme)
        theme_menu.addAction(light_theme_action)

        dark_theme_action = QAction('暗黑主题', self)
        dark_theme_action.triggered.connect(self.set_dark_theme)
        theme_menu.addAction(dark_theme_action)

    def start_server(self):
        """启动服务器"""
        self.file_server = FileServer()
        self.file_server.start()
        self.status_label.setText(f'服务器正在监听 IP: {self.file_server.host} 端口: {self.file_server.port}')
        self.status_bar.showMessage('服务器已启动')
        self.log_text.append('服务器已启动...')
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_server(self):
        """关闭服务器"""
        if self.file_server:
            self.file_server.stop()
            self.status_label.setText('服务器已停止')
            self.status_bar.showMessage('服务器已停止')
            self.log_text.append('服务器已停止...')
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def show_about(self):
        """显示关于信息"""
        self.log_text.append('关于：这是一个文件监控服务端程序，使用 PyQt5 构建。')

    def set_light_theme(self):
        """设置明亮主题"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
                color: black;
            }
            QLabel, QTextEdit, QPushButton {
                background-color: white;
                color: black;
            }
        """)
        self.status_bar.showMessage('已切换到明亮主题')

    def set_dark_theme(self):
        """设置暗黑主题"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2e2e2e;
                color: white;
            }
            QLabel, QTextEdit, QPushButton {
                background-color: #2e2e2e;
                color: white;
            }
        """)
        self.status_bar.showMessage('已切换到暗黑主题')

def main():
    app = QApplication(sys.argv)
    gui = ServerGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
