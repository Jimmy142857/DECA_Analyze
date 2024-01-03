import sys
import os
import subprocess
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSplitter, 
    QSpacerItem, QSizePolicy, QMessageBox)
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from model import ModelViewer
from camera import CameraApp

class IntegratedApp(QWidget):
    # 多线程  

    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.setWindowTitle("Picture to Model")
        self.setGeometry(100, 100, 1280, 960)

        # 创建主布局
        main_layout = QHBoxLayout()

        # 创建左侧布局
        left_layout = QVBoxLayout()

        # 添加相机应用到左侧布局
        self.camera_app = CameraApp()
        left_layout.addWidget(self.camera_app)

        # 创建右侧布局
        right_layout = QVBoxLayout()

        # 添加模型查看器到右侧布局
        self.model_viewer = ModelViewer()
        right_layout.addWidget(self.model_viewer)

        # 创建按钮布局
        button_layout = QVBoxLayout()

        # 创建一个弹簧，使得按钮位于两个模块中间
        spacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        button_layout.addItem(spacer)

        # 中间添加一个按钮
        reconstruct_button = QPushButton("三维重建", self)
        reconstruct_button.clicked.connect(self.reconstruct_3d)

        # 按钮字体设置
        font = reconstruct_button.font()
        font.setPointSize(16)               # 设置字体大小为16
        font.setBold(True)                  # 设置字体加粗
        reconstruct_button.setFont(font)

        button_layout.addWidget(reconstruct_button)

        # 创建一个弹簧，使得按钮位于两个模块中间
        spacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        button_layout.addItem(spacer)

        # 将左侧、按钮和右侧布局添加到主布局
        main_layout.addLayout(left_layout)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(right_layout)

        # 设置主窗口的布局
        self.setLayout(main_layout)

    def reconstruct_3d(self):
        """ 三维重建 """
        # 输入图片路径
        input_path = self.camera_app.input_path

        if not input_path:
            QMessageBox.warning(self, "警告", "没有选择图像或已拍摄图像未保存，请稍后重试！")
            return

        # 获取文件名和输出文件夹
        input_path = os.path.normpath(input_path)
        image_directory = os.path.dirname(input_path)
        file_name = os.path.splitext(os.path.basename(input_path))[0]
        output_folder = os.path.join(image_directory, file_name)

        self.model_viewer.cleanModel()                                               # 清除现有模型
        
        # demo_reconstruct.py的位置
        demo_script_path = os.path.normpath("C:\\Users\\Administrator\\Desktop\\DECA_Analyze\\demos\\demo_reconstruct.py")

        # 构建命令行命令
        command = f"python {demo_script_path} -i {input_path} -s {output_folder} --saveObj True"

        # 运行命令
        try:
            subprocess.run(command, shell=True, check=True)
            obj_path = os.path.join(output_folder, file_name, file_name + '.obj')    # 糙模型路径
            self.model_viewer.loadModel(obj_path)                                    # 加载模型
            QMessageBox.information(self, "成功", "三维重建完成!")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "错误", f"三维重建失败，错误信息: {e}")
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    integrated_app = IntegratedApp()
    integrated_app.show()
    sys.exit(app.exec_())
