import sys
import os
import cv2
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QWidget, QVBoxLayout,
    QAction, QFileDialog
)
from PyQt5.QtGui import QIcon, QPixmap, QImage  # 图标、图像等 GUI 相关类
from PyQt5.QtCore import Qt  # Qt 对齐方式、窗口常量等
from core.rtmpose_processor import RTMPoseProcessor

class SimpleWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # 调用父类构造函数

        self.setWindowTitle("Image Processor")  # 设置窗口标题
        self.resize(600, 600)  # 设置窗口初始大小
        self.setWindowIcon(QIcon())  # 设置窗口图标（可设置为 QIcon("icon.png")）

        # 只使用CPU设备
        self.device = 'cpu'

        # 设置默认模型模式
        self.model_mode = 'balanced'

        # 初始化RTMPose姿态处理器
        print(f"初始化RTMPose处理器 (模式: {self.model_mode}, 设备: {self.device})")
        self.pose_processor = RTMPoseProcessor(
            mode=self.model_mode,
            backend='onnxruntime',
            device=self.device
        )


        self.label = QLabel("Welcome to PyQt5")  # 顶部标签控件
        self.label.setAlignment(Qt.AlignCenter)  # 设置文本居中

        self.image_label = QLabel("Original Image")  # 原图显示区域
        self.image_label.setAlignment(Qt.AlignCenter)  # 图片居中显示
        self.image_label.setFixedSize(400, 250)  # 限制图片区域大小

        self.processed_label = QLabel("Processed Image")  # 处理后图像显示区域
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_label.setFixedSize(400, 250)

        self.upload_button = QPushButton("Upload Image")  # 上传图片按钮
        self.upload_button.clicked.connect(self.load_image)  # 按钮点击后执行 load_image()

        layout = QVBoxLayout()  # 垂直布局
        layout.addWidget(self.label)  # 添加顶部标签
        layout.addWidget(self.upload_button)  # 添加上传按钮
        layout.addWidget(self.image_label)  # 添加原图区域
        layout.addWidget(self.processed_label)  # 添加处理图区域

        container = QWidget()  # 创建主控件容器
        container.setLayout(layout)  # 应用布局
        self.setCentralWidget(container)  # 设置为窗口中心部件

        self.statusBar().showMessage("Ready")  # 初始化状态栏信息
        self._create_menu()  # 初始化菜单栏

    def _create_menu(self):
        menu_bar = self.menuBar()  # 获取窗口菜单栏对象
        file_menu = menu_bar.addMenu("File")  # 创建“File”菜单项

        exit_action = QAction("Exit", self)  # 创建“退出”菜单项
        exit_action.triggered.connect(self.close)  # 点击菜单项时关闭窗口
        file_menu.addAction(exit_action)  # 将菜单项添加到“File”菜单中

    def load_image(self):
        # 弹出文件选择框，返回选择的文件路径
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", os.getcwd(), "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.label.setText(f"Loaded: {os.path.basename(file_path)}")  # 顶部文字更新
            self.statusBar().showMessage("Image loaded. Processing...")  # 状态栏提示

            # 原图使用 QPixmap 显示（缩放适配标签尺寸）
            pixmap = QPixmap(file_path).scaled(
                self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio
            )
            self.image_label.setPixmap(pixmap)  # 设置原图标签内容

            # 使用 OpenCV 读取图像（默认 BGR 格式）
            img_bgr = cv2.imread(file_path)

            # 调用图像处理函数（你可以自定义处理逻辑）
            processed_bgr = self.process_image(img_bgr)

            rgb = processed_bgr
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            qt_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # 转为 QPixmap 并缩放显示
            pixmap_processed = QPixmap.fromImage(qt_img).scaled(
                self.processed_label.width(), self.processed_label.height(), Qt.KeepAspectRatio
            )
            self.processed_label.setPixmap(pixmap_processed)

            self.statusBar().showMessage("Processing done")  # 状态栏更新

    def process_image(self, image_bgr):
        """图像处理函数：你可以在这里添加自定义逻辑"""
        processed_frame = self.pose_processor.process_frame(image_bgr)
        return processed_frame

if __name__ == "__main__":
    app = QApplication(sys.argv)  # 创建应用对象
    window = SimpleWindow()  # 创建主窗口
    window.show()  # 显示窗口
    sys.exit(app.exec_())  # 启动事件循环