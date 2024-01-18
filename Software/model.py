import os, sys, vtk
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, 
    QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, 
    QLabel,
)
from PyQt5.QtGui import QPixmap, QColor
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.all import vtkTextActor


class ModelViewer(QWidget):
    def __init__(self): 
        super().__init__()
        self.initUI()

    def initUI(self):
        # 设置窗口标题和大小
        # self.setWindowTitle("3D Model 查看器")
        # self.setGeometry(100, 100, 640, 960)

        # 创建VTK渲染窗口交互器
        self.vtkWidget = QVTKRenderWindowInteractor(self)

        # 将vtkWidget添加到主窗口
        layout = QVBoxLayout()
        layout.addWidget(self.vtkWidget)

        # 创建水平布局
        buttonLayout = QHBoxLayout()

        # 创建一个按钮用于选择并加载模型
        loadButton = QPushButton("选择3D模型", self)
        loadButton.clicked.connect(self.chooseModel)
        buttonLayout.addWidget(loadButton)

        # 创建一个按钮用于重置视角
        resetViewButton = QPushButton("重置视角", self)
        resetViewButton.clicked.connect(self.resetView)
        buttonLayout.addWidget(resetViewButton)

        # 创建一个按钮用于清空模型
        cleanButton = QPushButton("清空", self)
        cleanButton.clicked.connect(self.cleanModel)
        buttonLayout.addWidget(cleanButton)

        # 将水平布局添加到主布局
        layout.addLayout(buttonLayout)

        frame = QFrame()
        frame.setLayout(layout)
        self.setLayout(layout)  # 将布局设置为主窗口的布局  

        # 初始化VTK渲染窗口
        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        # 创建一个文本标签用于显示模型名称
        self.fileNameActor = vtkTextActor()
        self.fileNameActor.GetTextProperty().SetFontSize(30)               # 设置文本字体大小
        self.fileNameActor.GetTextProperty().SetColor(1, 1, 1)             # 设置文本标签颜色为白色
        self.fileNameActor.GetTextProperty().SetJustificationToCentered()  # 设置文本对齐方式为居中
        self.fileNameActor.GetTextProperty().SetFontFamilyToArial()        # 设置字体为Arial

        # 连接渲染窗口大小变化事件
        self.vtkWidget.GetRenderWindow().AddObserver(vtk.vtkCommand.ModifiedEvent, self.onRenderWindowModified)
      
        # 启动交互器
        self.iren.Initialize()
        self.iren.Start()

    def onRenderWindowModified(self, obj, event):
        """ 文本位置调整 """
        # 获取渲染窗口的大小
        width, height = self.vtkWidget.GetRenderWindow().GetSize()

        # 更新文本标签位置
        self.fileNameActor.SetPosition(width / 2, 10)

        # 渲染
        self.iren.Render()

    def chooseModel(self):
        """ 选择三维模型 """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "选择3D模型文件", "", "3D模型文件 (*.obj);;所有文件 (*)", options=options)

        if fileName:
            # 清空之前加载的模型
            self.cleanModel()

            # 加载新的模型
            self.loadModel(fileName)

    def loadModel(self, file_path : str):
        """  加载三维模型, coarse含贴图, detail不含贴图 """
        # 获取 obj 文件所在的目录
        file_path = os.path.normpath(file_path)                 # 路径分隔符统一化
        obj_directory = os.path.dirname(file_path)

        # 设置当前工作目录为 obj 文件所在的目录
        os.chdir(obj_directory)

        # 模型文件名
        model_name = os.path.splitext(os.path.basename(file_path))[0]

        # mtl文件名
        mtl_path = file_path[:-3] + "mtl"

        # 贴图文件名
        texture_path = file_path[:-3] + "png"

        if os.path.exists(mtl_path) and os.path.exists(texture_path):
            # 使用vtkOBJImporter读取包含材质信息的.obj文件
            importer = vtk.vtkOBJImporter()
            importer.SetFileName(file_path)
            importer.Read()

            # 获取导入的Actor
            actor = importer.GetRenderer().GetActors().GetLastActor()
        else:
            # 使用vtkOBJReader读取.obj文件
            reader = vtk.vtkOBJReader()
            reader.SetFileName(file_path)

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(reader.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)

        # 将模型添加到渲染器中
        self.ren.AddActor(actor)
        self.ren.ResetCamera()

        # 更新文本标签内容
        self.fileNameActor.SetInput(model_name)        
        self.ren.AddActor2D(self.fileNameActor)  # 添加文本标签到渲染器

        # 启动交互器
        self.iren.Initialize()
        self.iren.Start()
                
    def resetView(self):
        """ 将相机状态恢复到初始状态 """
        self.ren.GetActiveCamera().SetViewUp(0, 1, 0)             # 设置上方向
        self.ren.GetActiveCamera().SetFocalPoint(0, 0, 0)         # 焦点设置到原点
        self.ren.GetActiveCamera().SetPosition(0, 0, 1)           # 相机位置设置到(0, 0, 1)

        self.ren.ResetCamera()
        self.iren.Render()

    def cleanModel(self):
        """ 清空选择的模型 """
        self.ren.RemoveAllViewProps()                             # 清空渲染器中的所有对象
        self.resetView()
        self.iren.Render()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = ModelViewer()
    mainWindow.show()
    sys.exit(app.exec_())
