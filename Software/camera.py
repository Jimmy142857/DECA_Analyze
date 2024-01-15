import sys, cv2, os, datetime
import face_alignment
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QImage, QPixmap, QColor, QPainter, QFont
from PyQt5.QtCore import QTimer, Qt, QLibraryInfo


os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = QLibraryInfo.location(            # 解决linux环境下Qt和CV的插件冲突
    QLibraryInfo.PluginsPath
)


class CameraApp(QWidget):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        # self.setWindowTitle("相机应用")
        # self.setGeometry(100, 100, 640, 480)

        # 创建布局
        main_layout = QVBoxLayout()

        # 人脸检测开关按钮
        self.face_detection_enabled = True
        self.face_detection_button = QPushButton("人脸检测", self)
        self.face_detection_button.setFixedSize(210, 40)
        self.face_detection_button.setCheckable(True)
        self.face_detection_button.setChecked(True)         # 默认开启人脸检测
        self.face_detection_button.clicked.connect(self.toggle_face_detection)

        # 关键点检测开关按钮
        self.lmk_detection_enable = False
        self.lmk_detection_button = QPushButton("关键点检测", self)
        self.lmk_detection_button.setFixedSize(210, 40)
        self.lmk_detection_button.setCheckable(True)
        self.lmk_detection_button.setChecked(False)         # 默认关闭关键点检测
        self.lmk_detection_button.clicked.connect(self.toggle_lmk_detection)

        # 关键点检测开关按钮
        self.face_segmentation_enable = False
        self.face_segmentation_button = QPushButton("人脸分割", self)
        self.face_segmentation_button.setFixedSize(210, 40)
        self.face_segmentation_button.setCheckable(True)
        self.face_segmentation_button.setChecked(False)      # 默认关闭人脸分割
        self.face_segmentation_button.clicked.connect(self.toggle_face_segmentation)

        # 创建拍照按钮
        self.capture_button = QPushButton("拍照", self)
        self.capture_button.setFixedSize(210, 40)          # 设置按钮宽度为210
        self.capture_button.clicked.connect(self.capture_image)

        # 创建保存按钮
        self.save_button = QPushButton("保存", self)
        self.save_button.setFixedSize(210, 40)
        self.save_button.clicked.connect(self.save_image)

        # 创建选择照片按钮
        self.select_button = QPushButton("选择照片", self)
        self.select_button.setFixedSize(210, 40)
        self.select_button.clicked.connect(self.select_photo)

        # 创建用于显示相机图像的标签
        self.camera_label = QLabel(self)

        # 创建用于显示照片的标签
        self.photo_label = QLabel(self)
        placeholder_pixmap = QPixmap(640, 480)
        placeholder_pixmap.fill(Qt.lightGray)               # 初始时使用浅灰色填充
        self.photo_label.setPixmap(placeholder_pixmap)

        # 创建水平布局，包含相机图像标签和照片标签
        camera_layout = QHBoxLayout()
        camera_layout.addWidget(self.camera_label)

        photo_layout = QHBoxLayout()
        photo_layout.addWidget(self.photo_label)

        # 创建水平布局，包含人脸检测按钮、关键点检测按钮、人脸分割按钮
        detection_layout = QHBoxLayout()
        detection_layout.addWidget(self.face_detection_button)
        detection_layout.addWidget(self.lmk_detection_button)
        detection_layout.addWidget(self.face_segmentation_button)

        # 创建水平布局，包含保存按钮、拍照按钮、选择按钮
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.capture_button)        
        input_layout.addWidget(self.save_button)
        input_layout.addWidget(self.select_button)

        # 将布局添加到垂直布局
        main_layout.addLayout(camera_layout)
        main_layout.addLayout(detection_layout)
        main_layout.addLayout(photo_layout)
        main_layout.addLayout(input_layout)

        # 设置按钮的对齐方式为左对齐
        input_layout.setAlignment(Qt.AlignLeft)
        detection_layout.setAlignment(Qt.AlignLeft)

        # 创建计时器，用于定期刷新显示的相机图像
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_camera_image)

        # 初始化相机
        self.cap = None                                                 # 初始化相机
        self.camera_available = False                                   # 新增标志
        
        camera_index = self.find_camera_index()                         # 获取相机id
        if camera_index is not None:
            self.cap = cv2.VideoCapture(camera_index)
            if self.cap.isOpened():
                print("Camera_index:", camera_index, ", Camera launch successfully.")
                self.camera_available = True                            # 设置标志为True
        else:
            print("No camera found.")

        # 创建人脸检测器
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # 创建人脸关键点检测器
        self.fa = face_alignment.FaceAlignment(landmarks_type = face_alignment.LandmarksType.TWO_D, flip_input=False)

        # 启动计时器，每20毫秒更新一次相机图像
        self.timer.start(20)

        # 初始化建模输入图片路径
        self.input_path = None

        # 初始化已拍摄照片
        self.captured_image = None

        # 初始化当前用户
        self.username = "adminstrator"

        # 设置布局
        self.setLayout(main_layout)

    def find_camera_index(self):
        """ 查找相机设备id """
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cap.release()
                return i
        return None

    def capture_image(self):
        """ 拍照按钮功能 """
        # 判断相机是否正常
        if not self.camera_available:
            QMessageBox.warning(self, "警告", "No camera avaliable!")
            return
        
        # 读取当前帧
        ret, frame = self.cap.read()

        # 将图像转换为Qt图像
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        qt_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)

        # 显示拍摄的照片
        self.photo_label.setPixmap(QPixmap.fromImage(qt_image))

        # 已拍摄的图像
        self.captured_image = image

        # 重置建模输入路径
        self.input_path = None

        # 启用保存按钮
        self.save_button.setEnabled(True)

    def update_camera_image(self):
        """ 刷新相机界面 """
        # 检查相机是否可用
        if not self.camera_available:
            # 如果相机不可用，使用占位符图像显示文本
            placeholder_pixmap = QPixmap(640, 480)
            placeholder_pixmap.fill(Qt.lightGray)

            painter = QPainter(placeholder_pixmap)
            font = QFont()
            font.setPointSize(20)
            painter.setFont(font)
            painter.drawText(200, 240, "No Camera Found")  # 调整文本位置
            painter.end()

            self.camera_label.setPixmap(placeholder_pixmap)
            return

        # 定期刷新显示的相机图像
        ret, frame = self.cap.read()

        # 在处理帧之前检查帧是否为空
        if not ret or frame is None:
            return

        # 人脸检测开关
        if self.face_detection_enabled:
            # 在图像中检测人脸
            faces = self.detect_faces(frame)
            for (x, y, w, h) in faces:
                # 绘制并调整人脸框的大小
                x, y, w, h = int(x + 0.1 * w), int(y + 0.1 * h), int(0.8 * w), int(0.8 * h)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # 关键点检测开关
        if self.lmk_detection_enable:
            # 在图像中检测人脸关键点
            landmarks = self.fa.get_landmarks(frame)
            if landmarks is not None:
                # 在图像上绘制关键点
                for point in landmarks[0]:
                    cv2.circle(frame, tuple(map(int, point)), 2, (0, 255, 0), -1)
            else:
                QMessageBox.warning(self, "提示", "未检测到人脸关键点，请看摄像头！")
        
        # 脸部分割开关
        if self.face_segmentation_enable:
            # 在图像中检测人脸关键点
            landmarks = self.fa.get_landmarks(frame)
            if landmarks is not None:
                landmarks_points = landmarks[0]

                # 获取眼睛、鼻子、嘴巴和眉毛的关键点坐标
                left_eye_points = landmarks_points[36:42]
                right_eye_points = landmarks_points[42:48]

                left_eyebrow_points = landmarks_points[17:22]
                right_eyebrow_points = landmarks_points[22:27]
                
                nose_points = landmarks_points[31:36]
                nose_points = np.append(nose_points, [landmarks_points[27]], axis=0)

                mouth_points = landmarks_points[48:68]

                cheek_points = landmarks_points[0:17]
                cheek_points = np.append(cheek_points, landmarks_points[26:16:-1], axis=0)

                # 画出脸颊区域（浅蓝色 ）
                self.draw_polygon(frame, cheek_points, color=(255, 255, 225))

                # 画出眼睛区域（蓝色）
                self.draw_polygon(frame, left_eye_points, color=(255, 0, 0))
                self.draw_polygon(frame, right_eye_points, color=(255, 0, 0))

                # 画出鼻子区域（红色）
                self.draw_polygon(frame, nose_points, color=(0, 0, 255))

                # 画出嘴巴区域（绿色）
                self.draw_polygon(frame, mouth_points, color=(0, 255, 0))

                # 画出眉毛区域（橙色）
                self.draw_polygon(frame, left_eyebrow_points, color=(0, 140, 255))
                self.draw_polygon(frame, right_eyebrow_points, color=(0, 140, 255))
            else:
                QMessageBox.warning(self, "提示", "无法进行面部分割，请看摄像头！")                
            

        # 将图像转换为Qt图像
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        qt_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)

        # 显示相机图像
        self.camera_label.setPixmap(QPixmap.fromImage(qt_image))

    def save_image(self):
        """ 保存图片 """
        if self.captured_image is None or not self.captured_image.any():
            QMessageBox.warning(self, "警告", "请先拍摄照片!")
            return
        
        # 弹出文件夹选择对话框
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        folder_path = QFileDialog.getExistingDirectory(self, "请选择保存文件夹", options=options)

        # 如果用户选择了保存位置，保存图像
        if folder_path:
            # 获取当前时间
            current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # 使用用户名和当前时间生成文件名
            file_name = f"{self.username}_{current_time}"
            file_path = os.path.normpath(os.path.join(folder_path, file_name + ".jpg"))
            cv2.imwrite(file_path, cv2.cvtColor(self.captured_image, cv2.COLOR_RGB2BGR))
            QMessageBox.information(self, "成功", f'图像已保存到：{file_path}')
            # 更新重建输入路径
            self.input_path = file_path

    def select_photo(self):
        """ 选择照片 """
        # 弹出文件选择对话框
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "选择照片", "", "图片文件 (*.png *.jpg *.bmp);;所有文件 (*)", options=options)

        # 如果用户选择了照片，显示在图片标签中
        if file_path:
            # 读取照片
            image = cv2.cvtColor(cv2.imread(file_path), cv2.COLOR_BGR2RGB)

            # 检查图像尺寸，如果太大，进行缩小
            max_width, max_height = 640, 480
            if image.shape[0] > max_height or image.shape[1] > max_width:
                scale_factor = min(max_width / image.shape[1], max_height / image.shape[0])
                image = cv2.resize(image, (int(image.shape[1] * scale_factor), int(image.shape[0] * scale_factor)))

            # 将图像转换为Qt图像
            qt_image = QImage(image.data, image.shape[1], image.shape[0], image.shape[1] * 3, QImage.Format_RGB888)
            # 显示照片
            self.photo_label.setPixmap(QPixmap.fromImage(qt_image))
            QMessageBox.information(self, "成功", f'已选取图像：{file_path}')

            # 保存已加载的图像
            self.captured_image = image
            # 更新重建输入路径
            self.input_path = file_path

            # 禁用保存按钮
            self.save_button.setEnabled(False)

    def detect_faces(self, frame):
        """ 在图像中检测人脸 """
        # 将帧转换为灰度图像
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 使用人脸级联检测器检测人脸
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return faces
    
    def draw_polygon(self, frame, points, color):
        """ 填充多边形 """
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.fillPoly(frame, [pts], color)

    def toggle_face_detection(self):
        """ 切换人脸检测状态 """
        self.face_detection_enabled = not self.face_detection_enabled

    def toggle_lmk_detection(self):
        """ 切换关键点检测状态 """
        self.lmk_detection_enable = not self.lmk_detection_enable

    def toggle_face_segmentation(self):
        """ 切换面部分割检测状态 """
        self.face_segmentation_enable = not self.face_segmentation_enable

    def closeEvent(self, event):
        # 关闭窗口时释放相机资源
        self.cap.release()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    camera_app = CameraApp()
    camera_app.show()
    sys.exit(app.exec_())
