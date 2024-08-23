from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QLabel, QDialog, QSlider
)
from PyQt5.QtCore import Qt

class FontSizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("调整字体大小")
        self.setGeometry(100, 100, 300, 100)
        
        layout = QVBoxLayout()

        # 添加滑块
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(8)
        self.slider.setMaximum(24)
        self.slider.setValue(12)  # 默认字体大小
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(2)
        self.slider.valueChanged.connect(self.update_font_size)

        layout.addWidget(QLabel("选择字体大小:"))
        layout.addWidget(self.slider)

        self.setLayout(layout)

    def update_font_size(self):
        """更新主窗口的字体大小"""
        font_size = self.slider.value()
        self.parent().set_font_size(font_size)
