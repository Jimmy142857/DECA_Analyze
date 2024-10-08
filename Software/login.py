from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QPushButton, QLabel, QMessageBox,
    QDialog, QDesktopWidget, QComboBox
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from main_app import IntegratedApp               # 导入主界面
from user_management import UserManagement       # 导入用户管理


class LoginWindow(QWidget):
    """ 登录界面 """
    login_successful = pyqtSignal()
    login_closed = pyqtSignal()

    def __init__(self, user_management, main_window):
        super().__init__()
        self.user_management = user_management
        self.main_window = main_window

        self.setWindowTitle("登录界面")
        self.setGeometry(0, 0, 360, 300)
        self.setWindowIcon(QIcon('Software/assets/login.png'))

        # 创建图片标签
        image_label = QLabel(self)
        pixmap = QPixmap("Software/assets/login.png")
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)

        # 创建用户名和密码的水平布局
        username_layout = QHBoxLayout()
        password_layout = QHBoxLayout()

        # 添加用户名和密码标签
        username_layout.addWidget(QLabel("用户名:"))
        password_layout.addWidget(QLabel("密码:"))

        # 添加用户名和密码输入框
        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)

        username_layout.addWidget(self.username_input)
        password_layout.addWidget(self.password_input)

        # 将水平布局嵌套到垂直布局中
        layout = QVBoxLayout(self)

        # 添加图片标签到垂直布局
        layout.addWidget(image_label)

        # 添加用户名和密码的水平布局
        layout.addLayout(username_layout)
        layout.addLayout(password_layout)

        # 添加按钮
        button_layout = QHBoxLayout()
        login_button = QPushButton("登录")
        cancel_button = QPushButton("返回")
        button_layout.addWidget(login_button)
        button_layout.addWidget(cancel_button)

        # 将按钮的水平布局添加到垂直布局中
        layout.addLayout(button_layout)

        # 连接按钮的点击事件
        login_button.clicked.connect(self.login)
        cancel_button.clicked.connect(self.reject)

        # 居中显示窗口
        self.center_on_screen()

    def center_on_screen(self):
        """将窗口居中显示"""
        screen_geometry = QDesktopWidget().availableGeometry()
        x = int((screen_geometry.width() - self.width()) / 2)
        y = int((screen_geometry.height() - self.height()) / 2)
        self.move(x, y)

    def login(self):
        """ 登录按钮逻辑 """
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "警告", "用户名和密码不能为空。")
            return

        if self.user_management.authenticate(username, password):
            QMessageBox.information(self, "提示", "登录成功")
            self.user_management.set_current_user(username)         # 设置当前用户
            self.clear_input()
            self.close()
            self.login_successful.emit()                            # 成功登录发送信号
            self.main_window.show()
        else:
            QMessageBox.warning(self, "警告", "用户名或密码错误")

    def reject(self):
        """ 返回按钮逻辑 """
        self.clear_input()
        self.close()
        self.login_closed.emit()

    def clear_input(self):
        """ 清空输入框 """   
        self.username_input.clear()  # 清空用户名输入框
        self.password_input.clear()  # 清空密码输入框


class RegisterWindow(QWidget):
    """ 注册界面 """
    registration_successful = pyqtSignal()
    registration_closed = pyqtSignal()

    def __init__(self, user_management, main_window):
        super().__init__()
        self.user_management = user_management
        self.main_window = main_window

        self.setWindowTitle("注册界面")
        self.setGeometry(0, 0, 360, 320)
        self.setWindowIcon(QIcon('Software/assets/register.png'))

        # 创建图片标签
        image_label = QLabel(self)
        pixmap = QPixmap("Software/assets/register.png")
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)

        # 创建用户名、年龄、性别、密码和确认密码的水平布局
        username_layout = QHBoxLayout()
        userage_layout = QHBoxLayout()
        usergender_layout = QHBoxLayout()
        password_layout = QHBoxLayout()
        confirm_password_layout = QHBoxLayout()

        # 添加用户名、年龄、性别、密码和确认密码的标签
        username_layout.addWidget(QLabel("用户名:"))
        userage_layout.addWidget(QLabel("年龄:"))
        usergender_layout.addWidget(QLabel("性别:"))
        password_layout.addWidget(QLabel("密码:"))
        confirm_password_layout.addWidget(QLabel("确认密码:"))

        # 添加用户名、密码和确认密码的输入框
        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.confirm_password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        # 使用QComboBox进行用户年龄、性别输入
        self.age_input = QComboBox(self)
        self.age_input.addItems([str(i) for i in range(1, 101)])
        self.gender_input = QComboBox(self)
        self.gender_input.addItems(["男", "女"])

        username_layout.addWidget(self.username_input)
        userage_layout.addWidget(self.age_input)
        usergender_layout.addWidget(self.gender_input)
        password_layout.addWidget(self.password_input)
        confirm_password_layout.addWidget(self.confirm_password_input)

        # 添加用户信息水平布局
        userinfo_layout = QHBoxLayout()
        userinfo_layout.addLayout(userage_layout)
        userinfo_layout.addLayout(usergender_layout)

        # 将水平布局嵌套到垂直布局中
        layout = QVBoxLayout(self)

        # 添加图片标签到垂直布局
        layout.addWidget(image_label)

        # 添加用户信息、密码和确认密码的水平布局
        layout.addLayout(username_layout)
        layout.addLayout(userinfo_layout)
        layout.addLayout(password_layout)
        layout.addLayout(confirm_password_layout)

        # 添加注册，返回按钮
        button_layout = QHBoxLayout()
        register_button = QPushButton("注册", self)
        cancel_button = QPushButton("返回", self)
        button_layout.addWidget(register_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        # 连接按钮的点击事件
        register_button.clicked.connect(self.register)
        cancel_button.clicked.connect(self.reject)

        # 居中显示窗口
        self.center_on_screen()

    def center_on_screen(self):
        """将窗口居中显示"""
        screen_geometry = QDesktopWidget().availableGeometry()
        x = int((screen_geometry.width() - self.width()) / 2)
        y = int((screen_geometry.height() - self.height()) / 2)
        self.move(x, y)

    def register(self):
        """ 注册按钮逻辑 """
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        age = self.age_input.currentText()
        gender = self.gender_input.currentText()

        if not username or not password or not confirm_password:
            QMessageBox.warning(self, "警告", "用户名和密码不能为空。")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "警告", "密码不一致，请重新输入。")
            return

        if self.user_management.register(username, password, age, gender):
            QMessageBox.information(self, "提示", "注册成功")
            self.user_management.set_current_user(username)         # 设置当前用户
            self.clear_input()
            self.close()
            self.registration_successful.emit()                     # 成功注册发送信号
            self.main_window.show()
        else:
            QMessageBox.warning(self, "警告", "用户名已存在，请选择其他用户名。")

    def reject(self):
        """ 返回按钮逻辑 """
        self.clear_input()
        self.close()
        self.registration_closed.emit()

    def clear_input(self):
        """ 清空输入框 """   
        self.username_input.clear()             # 清空用户名输入框
        self.password_input.clear()             # 清空密码输入框
        self.confirm_password_input.clear()     # 清空确认密码输入框
        self.age_input.setCurrentIndex(0)       # 将年龄输入框重置为默认值（例如第一个项目）
        self.gender_input.setCurrentIndex(0)    # 将性别输入框重置为默认值（例如第一个项目）


class RegisterLoginApp(QWidget):
    """ 欢迎界面 """
    def __init__(self):
        super().__init__()
        self.user_management = UserManagement()
        self.main_window = IntegratedApp(self.user_management)

        self.login_window = LoginWindow(self.user_management, self.main_window)
        self.register_window = RegisterWindow(self.user_management, self.main_window)

        # 将成功 登录/注册 的信号连接到 关闭主窗口/更新用户标签 的方法
        self.login_window.login_successful.connect(self.close)
        self.login_window.login_successful.connect(self.main_window.login_successful_handler)
        self.register_window.registration_successful.connect(self.close)
        self.register_window.registration_successful.connect(self.main_window.registration_successful_handler)

        # 将取消 登录/注册 的信号连接到显示主窗口的方法
        self.login_window.login_closed.connect(self.show)
        self.register_window.registration_closed.connect(self.show)

        # 将主界面用户注销的信号连接到显示主窗口的方法
        self.main_window.logout_successful.connect(self.show)

        # 设置窗口标题和大小
        self.setWindowTitle("欢迎")
        self.setGeometry(0, 0, 640, 480)
        self.setWindowIcon(QIcon('Software/assets/logo.png'))

        # 创建主布局
        main_layout = QVBoxLayout()

        # 添加图片标签
        image_label = QLabel(self)
        pixmap = QPixmap("Software/assets/logo.png")  # 欢迎图片
        image_label.setPixmap(pixmap)

        # 创建按钮布局
        button_layout = QHBoxLayout()

        self.login_button = QPushButton("登录", self)
        self.login_button.clicked.connect(self.show_login_window)

        self.register_button = QPushButton("注册", self)
        self.register_button.clicked.connect(self.show_register_window)

        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)

        # 将布局添加到主布局
        main_layout.addWidget(image_label, alignment=Qt.AlignTop | Qt.AlignHCenter)
        main_layout.addLayout(button_layout)

        # 设置主窗口的布局
        self.setLayout(main_layout)

        # 居中显示窗口
        self.center_on_screen()

    def center_on_screen(self):
        """将窗口居中显示"""
        screen_geometry = QDesktopWidget().availableGeometry()
        x = int((screen_geometry.width() - self.width()) / 2)
        y = int((screen_geometry.height() - self.height()) / 2)
        self.move(x, y)

    def show_login_window(self):
        """ 显示登录界面 """
        self.login_window.show()
        self.hide()

    def show_register_window(self):
        """ 显示注册界面 """
        self.register_window.show()
        self.hide()


if __name__ == '__main__':
    app = QApplication([])
    register_login_app = RegisterLoginApp()
    register_login_app.show()
    app.exec_()
