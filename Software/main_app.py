import os
import sys
import subprocess
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QFileDialog, QMessageBox, QSpacerItem,
    QSizePolicy, QDesktopWidget, QLabel, QDialog
)
from PyQt5.QtGui import QPixmap, QIcon, QFont
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from model import ModelViewer
from camera import CameraApp


class ReconstructionThread(QThread):
    """三维重建线程"""
    finished = pyqtSignal(str, str, str)            # 结束信号，用于在操作完成时发出通知

    def __init__(self, input_path, output_folder, file_name):
        super().__init__()
        self.input_path = input_path
        self.output_folder = output_folder
        self.file_name = file_name

    def run(self):
        try:
            # 执行三维重建代码
            demo_script_path = os.path.normpath("C:\\Users\\Administrator\\Desktop\\DECA_Analyze\\demos\\demo_reconstruct.py")
            command = f"python {demo_script_path} -i {self.input_path} -s {self.output_folder} --saveObj True"
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            # 发送错误信息
            self.finished.emit(f"三维重建失败，错误信息: {e}", "", "")
            return

        # 通知主线程操作完成
        self.finished.emit("", self.output_folder, self.file_name)
        
class UserInfoPopup(QDialog):
    """用户信息弹窗"""
    def __init__(self, user_management):
        super().__init__()

        # 获取用户信息
        current_user = user_management.get_current_user_info()

        # 创建标签显示用户信息
        username_label = QLabel(f"用户名: {current_user['username']}")
        gender_age_label = QLabel(f"性别: {current_user['gender']}   |  年龄: {current_user['age']}")
        registration_info_label = QLabel(f"注册ID: {current_user['id']}  |  注册时间: {current_user['created_at']}")

        # 创建布局
        layout = QVBoxLayout()
        layout.addWidget(username_label)
        layout.addWidget(gender_age_label)
        layout.addWidget(registration_info_label)

        self.setLayout(layout)
        self.setWindowTitle("用户信息")
        self.setWindowIcon(QIcon('Software/assets/logo.png'))

class IntegratedApp(QWidget):
    """ 主界面 """
    def __init__(self, user_management = None):
        super().__init__()
        # 添加重建成员变量
        self.reconstruction_thread = None

        # 用户管理成员变量
        self.user_management = user_management
        self.current_user = None

        # 设置窗口标题和大小
        self.setWindowTitle("三维人脸分析")
        self.setGeometry(0, 0, 1440, 960)
        self.setWindowIcon(QIcon('Software/assets/logo.png'))

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

        # 在按钮上方添加一个标签显示当前用户
        self.user_label = QLabel(f"欢迎你,管理员!")
        button_layout.addWidget(self.user_label, alignment=Qt.AlignTop | Qt.AlignHCenter)

        # 设置标签、按钮的字体
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.user_label.setFont(font)

        # 创建一个弹簧，使得按钮位于两个模块中间
        spacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        button_layout.addItem(spacer)

        # 中间添加一个按钮
        self.reconstruct_button = QPushButton("三维重建", self)
        self.reconstruct_button.clicked.connect(self.reconstruct_3d)
        self.reconstruct_button.setFont(font)                           # 按钮字体设置

        # 创建用户信息按钮
        self.user_info_button = QPushButton("用户信息", self)
        self.user_info_button.clicked.connect(self.show_user_info)
        self.user_info_button.setFont(font)

        # 创建用户信息按钮
        self.user_logout_button = QPushButton("退出", self)
        self.user_logout_button.clicked.connect(self.logout)
        self.user_logout_button.setFont(font)

        button_layout.addWidget(self.reconstruct_button)
        button_layout.addWidget(self.user_info_button)
        button_layout.addWidget(self.user_logout_button)

        # 创建一个弹簧，使得按钮位于两个模块中间
        spacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        button_layout.addItem(spacer)

        # 将左侧、按钮和右侧布局添加到主布局
        main_layout.addLayout(left_layout)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(right_layout)

        # 设置主窗口的布局
        self.setLayout(main_layout)

        # 居中显示窗口
        self.center_on_screen()

    def center_on_screen(self):
        """ 将窗口居中显示 """
        screen_geometry = QDesktopWidget().availableGeometry()
        x = int((screen_geometry.width() - self.width()) / 2)
        y = int((screen_geometry.height() - self.height()) / 2)
        self.move(x, y)

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

        self.model_viewer.cleanModel()  # 清除现有模型

        # 禁用按钮
        self.reconstruct_button.setEnabled(False)

        # 创建重建线程
        self.reconstruction_thread = ReconstructionThread(input_path, output_folder, file_name)
        self.reconstruction_thread.finished.connect(self.reconstruction_finished)  # 连接信号

        # 启动线程
        self.reconstruction_thread.start()

    def reconstruction_finished(self, error_message, output_folder, file_name):
        """ 重建结束 """
        # 恢复按钮状态
        self.reconstruct_button.setEnabled(True)

        if error_message:
            QMessageBox.critical(self, "错误", error_message)
        else:
            # 三维重建完成，执行界面更新
            obj_path = os.path.join(output_folder, file_name, file_name + '.obj')  # 糙模型路径
            self.model_viewer.loadModel(obj_path)  # 加载模型
            QMessageBox.information(self, "成功", "三维重建完成!")

    def update_user_label(self):
        """ 更新当前用户标签 """
        self.current_user = self.user_management.get_current_user()
        self.user_label.setText(f"欢迎你,{self.current_user}!")

    def login_successful_handler(self):
        """ 登录成功处理 """
        self.update_user_label()
        self.camera_app.username = self.current_user

    def registration_successful_handler(self):
        """ 注册成功处理 """
        self.update_user_label()
        self.camera_app.username = self.current_user

    def show_user_info(self):
        """ 显示用户信息弹窗 """
        if self.user_management:
            user_info_popup = UserInfoPopup(self.user_management)
            user_info_popup.exec_()

    def logout(self):
        """ 退出逻辑 """
        if self.user_management:
            self.user_management.close()        # 关闭数据库连接
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    integrated_app = IntegratedApp()
    integrated_app.show()
    sys.exit(app.exec_())
