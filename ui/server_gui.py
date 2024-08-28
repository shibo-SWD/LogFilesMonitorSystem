# server_gui.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QLabel, 
    QTextEdit, QStatusBar, QAction, QMenuBar, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from server.server_backend import FileServer
from ui.fonts import FontSizeDialog
import threading  # 导入线程库
import socket

class Communicator(QObject):
    # 定义信号
    status_update = pyqtSignal(str)
    log_update = pyqtSignal(str)
    server_started = pyqtSignal()
    server_stopped = pyqtSignal()

class ServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.file_server = None
        self.communicator = Communicator()
        self.current_theme = 'light'  # 初始化为明亮主题

        # 连接信号与槽
        self.communicator.status_update.connect(self.update_status_label)
        self.communicator.log_update.connect(self.update_log_text)
        self.communicator.server_started.connect(self.on_server_started)
        self.communicator.server_stopped.connect(self.on_server_stopped)

    def get_local_ip_address(self):
        """获取本地 IP 地址"""
        try:
            # 创建一个套接字来查找本地 IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except Exception as e:
            ip = "无法获取 IP"
        return ip

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

        # 将 QLabel 改为 QLineEdit 显示 IP 地址并设置为只读
        self.ip_line_edit = QLineEdit(self)
        self.ip_line_edit.setText(self.get_local_ip_address())
        self.ip_line_edit.setReadOnly(True)  # 设置为只读
        layout.addWidget(QLabel('本地 IP 地址:'))
        layout.addWidget(self.ip_line_edit)

        # 日志保存地址输入框
        self.save_dir_input = QLineEdit(self)
        self.save_dir_input.setText('./data/received_files')
        layout.addWidget(QLabel('监控日志保存地址:'))
        layout.addWidget(self.save_dir_input)

        # 启动和关闭按钮
        self.start_button = QPushButton('启动服务器')
        self.start_button.clicked.connect(self.start_server)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton('关闭服务器')
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_server)
        layout.addWidget(self.stop_button)

        # 日志显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

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

        # 添加字体调整选项
        settings_menu = menubar.addMenu('设置')
        font_action = QAction('调整字体大小', self)
        font_action.triggered.connect(self.open_font_size_dialog)
        settings_menu.addAction(font_action)

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
        save_dir_path = self.save_dir_input.text()  # 获取输入框中的文本
        
        # 检查输入是否为空，提供一个默认值
        if not save_dir_path:
            save_dir_path = './data/received_files'

        self.file_server = FileServer(save_dir=save_dir_path, log_signal=self.communicator.log_update)

        # 将服务器启动放在后台线程中，以免阻塞主线程
        threading.Thread(target=self._start_server_in_thread, daemon=True).start()

    def _start_server_in_thread(self):
        """后台线程中启动服务器"""
        self.file_server.start()
        # 通过信号更新 GUI
        self.communicator.status_update.emit(f'服务器正在监听 IP: {self.file_server.host} 端口: {self.file_server.port}')
        self.communicator.server_started.emit()

    def stop_server(self):
        """关闭服务器"""
        if self.file_server:
            self.file_server.stop()
            self.communicator.status_update.emit('服务器已停止')
            self.communicator.server_stopped.emit()

    def update_status_label(self, status_text):
        """更新状态标签"""
        self.status_label.setText(status_text)

    def update_log_text(self, log_text):
        """更新日志文本区域"""
        self.log_text.append(log_text)

    def on_server_started(self):
        """服务器启动后的处理"""
        self.status_bar.showMessage('服务器已启动')
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.communicator.log_update.emit('服务器已启动...')

    def on_server_stopped(self):
        """服务器停止后的处理"""
        self.status_bar.showMessage('服务器已停止')
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.communicator.log_update.emit('服务器已停止...')

    def show_about(self):
        """显示关于信息"""
        self.log_text.append('关于：这是一个文件监控服务端程序，使用 PyQt5 构建。')

    def set_light_theme(self):
        """设置明亮主题"""
        self.current_theme = 'light'  # 更新当前主题
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
        self.current_theme = 'dark'  # 更新当前主题
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2e2e2e;
                color: white;
            }
            QLabel, QTextEdit, QPushButton, QLineEdit {
                background-color: #2e2e2e;
                color: white;
                border: 1px solid #444;
            }
            QMenuBar {
                background-color: #2e2e2e;
                color: white;
            }
            QMenuBar::item {
                background-color: #2e2e2e;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #444;
            }
            QMenu {
                background-color: #2e2e2e;
                color: white;
            }
            QMenu::item:selected {
                background-color: #444;
            }
            QDialog {
                background-color: #2e2e2e;
                color: white;
            }
            QDialog QLabel, QDialog QPushButton, QDialog QLineEdit {
                background-color: #2e2e2e;
                color: white;
                border: 1px solid #444;
            }
        """)
        self.status_bar.showMessage('已切换到暗黑主题')

    def open_font_size_dialog(self):
        """打开字体大小调整对话框"""
        font_dialog = FontSizeDialog(self)
        font_dialog.exec_()

    def set_font_size(self, size):
        """设置整个应用的字体大小"""
        self.current_font_size = size
        # 根据当前主题设置字体大小
        if self.current_theme == 'dark':
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-color: #2e2e2e;
                    color: white;
                }}
                QLabel, QTextEdit, QPushButton, QLineEdit {{
                    background-color: #2e2e2e;
                    color: white;
                    border: 1px solid #444;
                }}
                QMenuBar {{
                    background-color: #2e2e2e;
                    color: white;
                }}
                QMenuBar::item {{
                    background-color: #2e2e2e;
                    color: white;
                }}
                QMenuBar::item:selected {{
                    background-color: #444;
                }}
                QMenu {{
                    background-color: #2e2e2e;
                    color: white;
                }}
                QMenu::item:selected {{
                    background-color: #444;
                }}
                QDialog {{
                    background-color: #2e2e2e;
                    color: white;
                }}
                QDialog QLabel, QDialog QPushButton, QDialog QLineEdit {{
                    background-color: #2e2e2e;
                    color: white;
                    border: 1px solid #444;
                }}
                * {{
                    font-size: {size}px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-color: white;
                    color: black;
                }}
                QLabel, QTextEdit, QPushButton {{
                    background-color: white;
                    color: black;
                }}
                * {{
                    font-size: {size}px;
                }}
            """)

