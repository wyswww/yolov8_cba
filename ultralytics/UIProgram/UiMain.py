# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 主布局
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # 左侧控制面板
        self.left_widget = QtWidgets.QWidget(self.centralwidget)
        self.left_widget.setMaximumSize(QtCore.QSize(350, 16777215))
        self.left_widget.setObjectName("left_widget")

        # 左侧垂直布局
        self.verticalLayout = QtWidgets.QVBoxLayout(self.left_widget)
        self.verticalLayout.setObjectName("verticalLayout")

        # 文件操作组
        self.file_group = QtWidgets.QGroupBox(self.left_widget)
        self.file_group.setObjectName("file_group")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.file_group)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        # 图片按钮
        self.PicBtn = QtWidgets.QPushButton(self.file_group)
        self.PicBtn.setObjectName("PicBtn")
        self.verticalLayout_2.addWidget(self.PicBtn)

        # 图片路径显示
        self.PiclineEdit = QtWidgets.QLineEdit(self.file_group)
        self.PiclineEdit.setReadOnly(True)
        self.PiclineEdit.setObjectName("PiclineEdit")
        self.verticalLayout_2.addWidget(self.PiclineEdit)

        # 视频按钮
        self.VideoBtn = QtWidgets.QPushButton(self.file_group)
        self.VideoBtn.setObjectName("VideoBtn")
        self.verticalLayout_2.addWidget(self.VideoBtn)

        # 视频路径显示
        self.VideolineEdit = QtWidgets.QLineEdit(self.file_group)
        self.VideolineEdit.setReadOnly(True)
        self.VideolineEdit.setObjectName("VideolineEdit")
        self.verticalLayout_2.addWidget(self.VideolineEdit)

        # 摄像头按钮
        self.CapBtn = QtWidgets.QPushButton(self.file_group)
        self.CapBtn.setObjectName("CapBtn")
        self.verticalLayout_2.addWidget(self.CapBtn)

        # 摄像头状态显示
        self.CaplineEdit = QtWidgets.QLineEdit(self.file_group)
        self.CaplineEdit.setReadOnly(True)
        self.CaplineEdit.setObjectName("CaplineEdit")
        self.verticalLayout_2.addWidget(self.CaplineEdit)

        # 批量处理按钮
        self.FilesBtn = QtWidgets.QPushButton(self.file_group)
        self.FilesBtn.setObjectName("FilesBtn")
        self.verticalLayout_2.addWidget(self.FilesBtn)

        self.verticalLayout.addWidget(self.file_group)

        # 检测信息组
        self.detect_group = QtWidgets.QGroupBox(self.left_widget)
        self.detect_group.setObjectName("detect_group")
        self.gridLayout = QtWidgets.QGridLayout(self.detect_group)
        self.gridLayout.setObjectName("gridLayout")

        # 目标选择下拉框
        self.comboBox = QtWidgets.QComboBox(self.detect_group)
        self.comboBox.setObjectName("comboBox")
        self.gridLayout.addWidget(self.comboBox, 0, 0, 1, 2)

        # 检测时间标签
        self.label_3 = QtWidgets.QLabel(self.detect_group)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        # 检测时间显示
        self.time_lb = QtWidgets.QLabel(self.detect_group)
        self.time_lb.setObjectName("time_lb")
        self.gridLayout.addWidget(self.time_lb, 1, 1, 1, 1)

        # 目标数量标签
        self.label_4 = QtWidgets.QLabel(self.detect_group)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)

        # 目标数量显示
        self.label_nums = QtWidgets.QLabel(self.detect_group)
        self.label_nums.setObjectName("label_nums")
        self.gridLayout.addWidget(self.label_nums, 2, 1, 1, 1)

        # 目标类型标签
        self.label_5 = QtWidgets.QLabel(self.detect_group)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)

        # 目标类型显示
        self.type_lb = QtWidgets.QLabel(self.detect_group)
        self.type_lb.setObjectName("type_lb")
        self.gridLayout.addWidget(self.type_lb, 3, 1, 1, 1)

        # 置信度标签
        self.label_6 = QtWidgets.QLabel(self.detect_group)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 4, 0, 1, 1)

        # 置信度显示
        self.label_conf = QtWidgets.QLabel(self.detect_group)
        self.label_conf.setObjectName("label_conf")
        self.gridLayout.addWidget(self.label_conf, 4, 1, 1, 1)

        # 坐标标签
        self.label_7 = QtWidgets.QLabel(self.detect_group)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 5, 0, 1, 1)

        # xmin显示
        self.label_xmin = QtWidgets.QLabel(self.detect_group)
        self.label_xmin.setObjectName("label_xmin")
        self.gridLayout.addWidget(self.label_xmin, 5, 1, 1, 1)

        # ymin显示
        self.label_ymin = QtWidgets.QLabel(self.detect_group)
        self.label_ymin.setObjectName("label_ymin")
        self.gridLayout.addWidget(self.label_ymin, 6, 1, 1, 1)

        # xmax显示
        self.label_xmax = QtWidgets.QLabel(self.detect_group)
        self.label_xmax.setObjectName("label_xmax")
        self.gridLayout.addWidget(self.label_xmax, 7, 1, 1, 1)

        # ymax显示
        self.label_ymax = QtWidgets.QLabel(self.detect_group)
        self.label_ymax.setObjectName("label_ymax")
        self.gridLayout.addWidget(self.label_ymax, 8, 1, 1, 1)

        # 类别统计进度条
        # self.progressBar = QtWidgets.QProgressBar(self.detect_group)
        # self.progressBar.setProperty("value", 0)
        # self.progressBar.setObjectName("progressBar")
        # self.gridLayout.addWidget(self.progressBar, 9, 0, 1, 2)
        #
        # self.progressBar_2 = QtWidgets.QProgressBar(self.detect_group)
        # self.progressBar_2.setProperty("value", 0)
        # self.progressBar_2.setObjectName("progressBar_2")
        # self.gridLayout.addWidget(self.progressBar_2, 10, 0, 1, 2)
        #
        # # 类别统计标签
        # self.label_20 = QtWidgets.QLabel(self.detect_group)
        # self.label_20.setObjectName("label_20")
        # self.gridLayout.addWidget(self.label_20, 9, 2, 1, 1)
        #
        # self.label_21 = QtWidgets.QLabel(self.detect_group)
        # self.label_21.setObjectName("label_21")
        # self.gridLayout.addWidget(self.label_21, 10, 2, 1, 1)

        self.verticalLayout.addWidget(self.detect_group)

        # 操作按钮组
        self.btn_group = QtWidgets.QGroupBox(self.left_widget)
        self.btn_group.setObjectName("btn_group")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.btn_group)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        # 保存按钮
        self.SaveBtn = QtWidgets.QPushButton(self.btn_group)
        self.SaveBtn.setObjectName("SaveBtn")
        self.verticalLayout_3.addWidget(self.SaveBtn)

        # 退出按钮
        self.ExitBtn = QtWidgets.QPushButton(self.btn_group)
        self.ExitBtn.setObjectName("ExitBtn")
        self.verticalLayout_3.addWidget(self.ExitBtn)

        self.verticalLayout.addWidget(self.btn_group)

        self.horizontalLayout.addWidget(self.left_widget)

        # 右侧显示区域
        self.right_widget = QtWidgets.QWidget(self.centralwidget)
        self.right_widget.setObjectName("right_widget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.right_widget)
        self.verticalLayout_4.setObjectName("verticalLayout_4")

        # 图像显示区域
        self.label_show = QtWidgets.QLabel(self.right_widget)
        self.label_show.setAlignment(QtCore.Qt.AlignCenter)
        self.label_show.setObjectName("label_show")
        self.verticalLayout_4.addWidget(self.label_show)

        # 检测结果表格
        self.tableWidget = QtWidgets.QTableWidget(self.right_widget)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "路径", "类别", "置信度", "位置"])
        self.verticalLayout_4.addWidget(self.tableWidget)

        self.horizontalLayout.addWidget(self.right_widget)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "目标检测系统"))

        # 文件操作组
        self.file_group.setTitle(_translate("MainWindow", "文件操作"))
        self.PicBtn.setText(_translate("MainWindow", "打开图片"))
        self.VideoBtn.setText(_translate("MainWindow", "打开视频"))
        self.CapBtn.setText(_translate("MainWindow", "打开摄像头"))
        self.FilesBtn.setText(_translate("MainWindow", "批量检测图片"))
        self.PiclineEdit.setPlaceholderText(_translate("MainWindow", "图片路径"))
        self.VideolineEdit.setPlaceholderText(_translate("MainWindow", "视频路径"))
        self.CaplineEdit.setPlaceholderText(_translate("MainWindow", "摄像头状态"))

        # 检测信息组
        self.detect_group.setTitle(_translate("MainWindow", "检测信息"))
        self.label_3.setText(_translate("MainWindow", "检测时间:"))
        self.time_lb.setText(_translate("MainWindow", "0.000 s"))
        self.label_4.setText(_translate("MainWindow", "目标数量:"))
        self.label_nums.setText(_translate("MainWindow", "0"))
        self.label_5.setText(_translate("MainWindow", "目标类型:"))
        self.type_lb.setText(_translate("MainWindow", ""))
        self.label_6.setText(_translate("MainWindow", "置信度:"))
        self.label_conf.setText(_translate("MainWindow", ""))
        self.label_7.setText(_translate("MainWindow", "坐标位置:"))
        self.label_xmin.setText(_translate("MainWindow", ""))
        self.label_ymin.setText(_translate("MainWindow", ""))
        self.label_xmax.setText(_translate("MainWindow", ""))
        self.label_ymax.setText(_translate("MainWindow", ""))
        # self.label_20.setText(_translate("MainWindow", "0%"))
        # self.label_21.setText(_translate("MainWindow", "0%"))

        # 操作按钮组
        self.btn_group.setTitle(_translate("MainWindow", "操作"))
        self.SaveBtn.setText(_translate("MainWindow", "保存结果"))
        self.ExitBtn.setText(_translate("MainWindow", "退出系统"))

        # 显示区域
        self.label_show.setText(_translate("MainWindow", "图像显示区域"))