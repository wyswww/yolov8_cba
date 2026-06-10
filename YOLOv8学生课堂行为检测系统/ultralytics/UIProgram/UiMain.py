# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1400, 950)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # ==================== 主布局（垂直） ====================
        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_layout.setObjectName("main_layout")
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(6)

        # ==================== 1. 图像显示区域（占主要空间） ====================
        self.image_container = QtWidgets.QWidget(self.centralwidget)
        self.image_container.setObjectName("image_container")
        self.image_layout = QtWidgets.QVBoxLayout(self.image_container)
        self.image_layout.setContentsMargins(0, 0, 0, 0)
        self.image_layout.setSpacing(2)

        # 缩放工具栏
        self.zoom_toolbar = QtWidgets.QWidget(self.image_container)
        self.zoom_toolbar.setObjectName("zoom_toolbar")
        self.zoom_toolbar.setMaximumHeight(32)
        self.zoom_layout = QtWidgets.QHBoxLayout(self.zoom_toolbar)
        self.zoom_layout.setContentsMargins(4, 0, 4, 0)
        self.zoom_layout.setSpacing(4)

        self.zoom_plus_btn = QtWidgets.QPushButton("＋")
        self.zoom_plus_btn.setObjectName("zoom_plus_btn")
        self.zoom_plus_btn.setFixedSize(28, 28)
        self.zoom_plus_btn.setToolTip("放大")

        self.zoom_minus_btn = QtWidgets.QPushButton("－")
        self.zoom_minus_btn.setObjectName("zoom_minus_btn")
        self.zoom_minus_btn.setFixedSize(28, 28)
        self.zoom_minus_btn.setToolTip("缩小")

        self.zoom_fit_btn = QtWidgets.QPushButton("⊡")
        self.zoom_fit_btn.setObjectName("zoom_fit_btn")
        self.zoom_fit_btn.setFixedSize(28, 28)
        self.zoom_fit_btn.setToolTip("适应窗口")

        self.zoom_label = QtWidgets.QLabel("100%")
        self.zoom_label.setObjectName("zoom_label")
        self.zoom_label.setFixedWidth(45)
        self.zoom_label.setAlignment(QtCore.Qt.AlignCenter)

        self.zoom_layout.addWidget(self.zoom_plus_btn)
        self.zoom_layout.addWidget(self.zoom_minus_btn)
        self.zoom_layout.addWidget(self.zoom_fit_btn)
        self.zoom_layout.addWidget(self.zoom_label)
        self.zoom_layout.addStretch()

        self.image_layout.addWidget(self.zoom_toolbar)

        # 可缩放图像视图
        self.graphicsView = QtWidgets.QGraphicsView(self.image_container)
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        self.graphicsView.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.graphicsView.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.graphicsView.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.graphicsView.setViewportUpdateMode(QtWidgets.QGraphicsView.SmartViewportUpdate)
        self.graphicsView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.graphicsView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.graphicsView.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.graphicsView.setBackgroundBrush(QtGui.QBrush(QtGui.QColor("#f0f0f0")))
        self._zoom_scene = QtWidgets.QGraphicsScene(self.graphicsView)
        self.graphicsView.setScene(self._zoom_scene)

        self.image_layout.addWidget(self.graphicsView)
        self.main_layout.addWidget(self.image_container, stretch=3)

        # 保留旧 name 兼容
        self.label_show = self.graphicsView

        # ==================== 2. 控制面板（按钮 + 检测信息） ====================
        self.control_panel = QtWidgets.QWidget(self.centralwidget)
        self.control_panel.setObjectName("control_panel")
        self.control_panel.setMaximumHeight(140)
        self.control_layout = QtWidgets.QHBoxLayout(self.control_panel)
        self.control_layout.setContentsMargins(0, 2, 0, 2)
        self.control_layout.setSpacing(8)

        # ---- 2a. 文件操作按钮组 ----
        self.file_group = QtWidgets.QGroupBox(self.control_panel)
        self.file_group.setObjectName("file_group")
        self.file_btn_layout = QtWidgets.QHBoxLayout(self.file_group)
        self.file_btn_layout.setContentsMargins(6, 4, 6, 4)
        self.file_btn_layout.setSpacing(6)

        self.PicBtn = QtWidgets.QPushButton(self.file_group)
        self.PicBtn.setObjectName("PicBtn")
        self.PicBtn.setMinimumWidth(80)
        self.file_btn_layout.addWidget(self.PicBtn)

        self.VideoBtn = QtWidgets.QPushButton(self.file_group)
        self.VideoBtn.setObjectName("VideoBtn")
        self.VideoBtn.setMinimumWidth(80)
        self.file_btn_layout.addWidget(self.VideoBtn)

        self.CapBtn = QtWidgets.QPushButton(self.file_group)
        self.CapBtn.setObjectName("CapBtn")
        self.CapBtn.setMinimumWidth(80)
        self.file_btn_layout.addWidget(self.CapBtn)

        self.FilesBtn = QtWidgets.QPushButton(self.file_group)
        self.FilesBtn.setObjectName("FilesBtn")
        self.FilesBtn.setMinimumWidth(80)
        self.file_btn_layout.addWidget(self.FilesBtn)

        self.control_layout.addWidget(self.file_group)

        # ---- 2b. 路径/状态只读显示 ----
        self.path_group = QtWidgets.QGroupBox(self.control_panel)
        self.path_group.setObjectName("path_group")
        self.path_layout = QtWidgets.QVBoxLayout(self.path_group)
        self.path_layout.setContentsMargins(6, 4, 6, 4)
        self.path_layout.setSpacing(2)

        self.PiclineEdit = QtWidgets.QLineEdit(self.path_group)
        self.PiclineEdit.setReadOnly(True)
        self.PiclineEdit.setObjectName("PiclineEdit")
        self.PiclineEdit.setMaximumHeight(22)
        self.path_layout.addWidget(self.PiclineEdit)

        self.VideolineEdit = QtWidgets.QLineEdit(self.path_group)
        self.VideolineEdit.setReadOnly(True)
        self.VideolineEdit.setObjectName("VideolineEdit")
        self.VideolineEdit.setMaximumHeight(22)
        self.path_layout.addWidget(self.VideolineEdit)

        self.CaplineEdit = QtWidgets.QLineEdit(self.path_group)
        self.CaplineEdit.setReadOnly(True)
        self.CaplineEdit.setObjectName("CaplineEdit")
        self.CaplineEdit.setMaximumHeight(22)
        self.path_layout.addWidget(self.CaplineEdit)

        self.control_layout.addWidget(self.path_group, stretch=1)

        # ---- 2c. 检测信息组 ----
        self.detect_group = QtWidgets.QGroupBox(self.control_panel)
        self.detect_group.setObjectName("detect_group")
        self.detect_grid = QtWidgets.QGridLayout(self.detect_group)
        self.detect_grid.setContentsMargins(6, 4, 6, 4)
        self.detect_grid.setSpacing(2)
        self.detect_grid.setObjectName("detect_grid")

        self.comboBox = QtWidgets.QComboBox(self.detect_group)
        self.comboBox.setObjectName("comboBox")
        self.detect_grid.addWidget(self.comboBox, 0, 0, 1, 4)

        self.label_3 = QtWidgets.QLabel(self.detect_group)
        self.label_3.setObjectName("label_3")
        self.detect_grid.addWidget(self.label_3, 1, 0, 1, 1)
        self.time_lb = QtWidgets.QLabel(self.detect_group)
        self.time_lb.setObjectName("time_lb")
        self.detect_grid.addWidget(self.time_lb, 1, 1, 1, 1)

        self.label_4 = QtWidgets.QLabel(self.detect_group)
        self.label_4.setObjectName("label_4")
        self.detect_grid.addWidget(self.label_4, 1, 2, 1, 1)
        self.label_nums = QtWidgets.QLabel(self.detect_group)
        self.label_nums.setObjectName("label_nums")
        self.detect_grid.addWidget(self.label_nums, 1, 3, 1, 1)

        self.label_5 = QtWidgets.QLabel(self.detect_group)
        self.label_5.setObjectName("label_5")
        self.detect_grid.addWidget(self.label_5, 2, 0, 1, 1)
        self.type_lb = QtWidgets.QLabel(self.detect_group)
        self.type_lb.setObjectName("type_lb")
        self.detect_grid.addWidget(self.type_lb, 2, 1, 1, 1)

        self.label_6 = QtWidgets.QLabel(self.detect_group)
        self.label_6.setObjectName("label_6")
        self.detect_grid.addWidget(self.label_6, 2, 2, 1, 1)
        self.label_conf = QtWidgets.QLabel(self.detect_group)
        self.label_conf.setObjectName("label_conf")
        self.detect_grid.addWidget(self.label_conf, 2, 3, 1, 1)

        self.label_7 = QtWidgets.QLabel(self.detect_group)
        self.label_7.setObjectName("label_7")
        self.detect_grid.addWidget(self.label_7, 3, 0, 1, 1)
        self.label_xmin = QtWidgets.QLabel(self.detect_group)
        self.label_xmin.setObjectName("label_xmin")
        self.detect_grid.addWidget(self.label_xmin, 3, 1, 1, 1)
        self.label_ymin = QtWidgets.QLabel(self.detect_group)
        self.label_ymin.setObjectName("label_ymin")
        self.detect_grid.addWidget(self.label_ymin, 3, 2, 1, 1)
        self.label_xmax = QtWidgets.QLabel(self.detect_group)
        self.label_xmax.setObjectName("label_xmax")
        self.detect_grid.addWidget(self.label_xmax, 4, 1, 1, 1)
        self.label_ymax = QtWidgets.QLabel(self.detect_group)
        self.label_ymax.setObjectName("label_ymax")
        self.detect_grid.addWidget(self.label_ymax, 4, 2, 1, 1)

        self.control_layout.addWidget(self.detect_group)

        # ---- 2d. 操作按钮组 ----
        self.btn_group = QtWidgets.QGroupBox(self.control_panel)
        self.btn_group.setObjectName("btn_group")
        self.btn_layout = QtWidgets.QVBoxLayout(self.btn_group)
        self.btn_layout.setContentsMargins(6, 4, 6, 4)
        self.btn_layout.setSpacing(4)

        self.SaveBtn = QtWidgets.QPushButton(self.btn_group)
        self.SaveBtn.setObjectName("SaveBtn")
        self.SaveBtn.setMinimumWidth(80)
        self.btn_layout.addWidget(self.SaveBtn)

        self.ExitBtn = QtWidgets.QPushButton(self.btn_group)
        self.ExitBtn.setObjectName("ExitBtn")
        self.ExitBtn.setMinimumWidth(80)
        self.btn_layout.addWidget(self.ExitBtn)

        self.control_layout.addWidget(self.btn_group)

        self.main_layout.addWidget(self.control_panel, stretch=0)

        # ==================== 3. 检测结果表格 ====================
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "路径", "类别", "置信度", "位置"])
        self.main_layout.addWidget(self.tableWidget, stretch=1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "专注度检测"))

        self.file_group.setTitle(_translate("MainWindow", "文件操作"))
        self.PicBtn.setText(_translate("MainWindow", "打开图片"))
        self.VideoBtn.setText(_translate("MainWindow", "打开视频"))
        self.CapBtn.setText(_translate("MainWindow", "打开摄像头"))
        self.FilesBtn.setText(_translate("MainWindow", "批量检测"))
        self.PiclineEdit.setPlaceholderText(_translate("MainWindow", "图片路径"))
        self.VideolineEdit.setPlaceholderText(_translate("MainWindow", "视频路径"))
        self.CaplineEdit.setPlaceholderText(_translate("MainWindow", "摄像头状态"))
        self.path_group.setTitle(_translate("MainWindow", "状态"))

        self.detect_group.setTitle(_translate("MainWindow", "检测信息"))
        self.label_3.setText(_translate("MainWindow", "时间:"))
        self.time_lb.setText(_translate("MainWindow", "0.000s"))
        self.label_4.setText(_translate("MainWindow", "人数:"))
        self.label_nums.setText(_translate("MainWindow", "0"))
        self.label_5.setText(_translate("MainWindow", "类型:"))
        self.type_lb.setText(_translate("MainWindow", ""))
        self.label_6.setText(_translate("MainWindow", "置信度:"))
        self.label_conf.setText(_translate("MainWindow", ""))
        self.label_7.setText(_translate("MainWindow", "坐标:"))
        self.label_xmin.setText(_translate("MainWindow", ""))
        self.label_ymin.setText(_translate("MainWindow", ""))
        self.label_xmax.setText(_translate("MainWindow", ""))
        self.label_ymax.setText(_translate("MainWindow", ""))

        self.btn_group.setTitle(_translate("MainWindow", "操作"))
        self.SaveBtn.setText(_translate("MainWindow", "保存结果"))
        self.ExitBtn.setText(_translate("MainWindow", "退出系统"))

        placeholder = self._zoom_scene.addText("图像显示区域")
        placeholder.setDefaultTextColor(QtGui.QColor("#999999"))
