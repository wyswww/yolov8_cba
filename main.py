# -*- coding: utf-8 -*-
import torch
#2026.4.23更新
torch.set_default_tensor_type('torch.FloatTensor')
import torch.serialization

torch.serialization.add_safe_globals([torch.nn.modules.container.Sequential])

# ====================== 强制修复权重加载 ======================
_original_torch_load = torch.load


def patched_torch_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)


torch.load = patched_torch_load
# ==============================================================

import os
import sys
import time
import cv2
import numpy as np
from PIL import ImageFont
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QCoreApplication
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog,
                             QMessageBox, QHeaderView, QTableWidgetItem, QAbstractItemView)
from ultralytics import YOLO

# 自定义模块
sys.path.append('UIProgram')
from UIProgram.UiMain import Ui_MainWindow
from UIProgram.QssLoader import QSSLoader
from UIProgram.precess_bar import ProgressBar
import detect_tools as tools
import Config

# ====================== 【极简美化】不影响任何功能 ======================
LIGHT_STYLE = """
QPushButton {
    background-color: #4a6cf7;
    color: white;
    border-radius: 5px;
    padding: 4px 8px;
}
QPushButton:hover {
    background-color: #3b5bdb;
}
QTableWidget {
    background-color: #ffffff;
}
QHeaderView::section {
    background-color: #edf1f7;
}
QMainWindow {
    background-color: #f5f7fa;
}

/* ------------- 只放大专注度显示标签 ------------- */
QLabel#label_nums {
    font-size: 16px;



}
"""

# ====================== 专注度算法增强版 ======================
# 三个维度综合计算：
#   1. 置信度加权    — 基础分 × 检测置信度
#   2. 时序行为分析  — 持续 N 帧分心 → 累进惩罚
#   3. 班级趋势分析  — 全班趋势上升/下降缓冲

RECENT_FRAMES = 15   # 追踪最近多少帧
PERSIST_THRESHOLD = 3  # 连续低专注度帧数阈值
PERSIST_PENALTY = 0.5  # 每多一帧额外惩罚值（封顶 3.0）
LOW_FOCUS_THRESHOLD = 5.0  # 低专注度阈值
TREND_ALPHA = 0.15       # 趋势缓冲系数
TREND_WEIGHT = 0.08      # 趋势占总分的权重
IOU_THRESHOLD = 0.4      # 匹配阈值，提高减少误判


class FocusTracker:
    """
    负责追踪每个学生（按检测框位置匹配）在视频流中的行为历史，
    计算时序惩罚和班级趋势。
    """

    def __init__(self, max_frames=RECENT_FRAMES):
        self.max_frames = max_frames
        # 结构: { 学生ID: [最近N帧的分数列表] }
        self._student_history: dict[int, list[float]] = {}
        # 全班历史均值，用于趋势计算
        self._class_avg_history: list[float] = []
        # 上一帧的检测框（用于IoU匹配）
        self._prev_boxes: dict[int, list] = {}

    # ---------------------- 位置匹配 ----------------------
    @staticmethod
    def _iou(box_a, box_b):
        """计算两个框的交并比，用于判断是否为同一个学生"""
        x1 = max(box_a[0], box_b[0])
        y1 = max(box_a[1], box_b[1])
        x2 = min(box_a[2], box_b[2])
        y2 = min(box_a[3], box_b[3])
        if x2 <= x1 or y2 <= y1:
            return 0.0
        inter = (x2 - x1) * (y2 - y1)
        area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
        area_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
        union = area_a + area_b - inter
        return inter / union if union > 0 else 0.0

    def _match_and_update(self, boxes, scores):
        """
        将新检测结果匹配到已有历史，删除长期未匹配的学生。
        boxes: 当前帧所有检测框
        scores: 当前帧所有基础专注度分数
        """
        used = set()
        new_history: dict[int, list[float]] = {}
        current_prev_boxes = {}

        for idx, box in enumerate(boxes):
            best_iou, best_key = 0.0, None
            for key in self._student_history:
                if key in used:
                    continue
                iou = self._iou(box, self._prev_boxes.get(key, box))
                if iou > best_iou:
                    best_iou = iou
                    best_key = key

            s = scores[idx]
            if best_key is not None and best_iou > 0.3:
                # 匹配成功，追加新数据
                hist = self._student_history[best_key]
                hist.append(s)
                if len(hist) > self.max_frames:
                    hist.pop(0)
                new_history[best_key] = hist
                current_prev_boxes[best_key] = box
                used.add(best_key)
            else:
                # 新学生，从单帧开始
                new_id = idx + 1000
                new_history[new_id] = [s]
                current_prev_boxes[new_id] = box

        # 保留未匹配但仍在窗口内的学生（短暂消失不删除）
        for key, hist in self._student_history.items():
            if key not in used and len(hist) < self.max_frames * 2:
                # 补一帧中性分延缓衰减
                hist.append(5.0)
                if len(hist) > self.max_frames:
                    hist.pop(0)
                new_history[key] = hist
                # 框位置保持不变或从 prev 获取
                current_prev_boxes[key] = self._prev_boxes.get(key, [0,0,0,0])

        self._student_history = new_history
        self._prev_boxes = current_prev_boxes

    # ---------------------- 核心计算 ----------------------
    def compute(self, boxes, classes, confidences):
        """
        主入口：输入当前帧检测结果，返回最终专注度评分 (0~10)。
        """
        n = len(boxes)
        if n == 0:
            self._class_avg_history.append(0.0)
            self._class_avg_history = self._class_avg_history[-50:]
            return 0, 0.0

        # 1. 计算基础分（置信度加权）
        base_scores = []
        for cls_name, conf in zip(
                [Config.names[c] for c in classes],
                confidences
        ):
            base = self._base_focus_from_class(cls_name)
            base_scores.append(base * conf)

        # 2. 时序匹配与更新
        self._match_and_update(boxes, base_scores)

        # 3. 时序惩罚
        final_scores = []
        for hist in self._student_history.values():
            penalty = self._temporal_penalty(hist)
            # 取最近一帧的分数应用惩罚
            latest = hist[-1]
            latest = max(0.0, latest - penalty)
            final_scores.append(latest)

        # 4. 班级均值 & 趋势
        avg = sum(final_scores) / len(final_scores)
        self._class_avg_history.append(avg)
        self._class_avg_history = self._class_avg_history[-50:]
        trend_adjusted = self._apply_trend(avg)

        return n, round(trend_adjusted, 2)

    @staticmethod
    def _base_focus_from_class(cls_name):
        """纯行为类别的基准专注度"""
        high = {"reading", "writing", "hand-raising"}
        mid  = {"bowing the head"}
        low  = {"leaning over the table", "using phone"}
        if cls_name in high:  return 8.5
        if cls_name in mid:   return 5.0
        if cls_name in low:   return 2.0
        return 5.5

    def _temporal_penalty(self, hist):
        """计算时序惩罚：持续分心越久，惩罚越重"""
        window = hist[-PERSIST_THRESHOLD:]
        count = sum(1 for s in window if s < 4.0)
        extra = max(0, count - PERSIST_THRESHOLD)
        return min(extra * PERSIST_PENALTY, 2.0)

    def _apply_trend(self, raw_avg):
        """趋势缓冲：班级专注度呈上升趋势时加分，下降时减分"""
        if len(self._class_avg_history) < 3:
            return raw_avg

        recent = self._class_avg_history[-5:]
        n = len(recent)
        mean_x = sum(range(n)) / n
        mean_y = sum(recent) / n
        slope = sum((recent[i] - mean_y) * (i - mean_x) for i in range(n)) / (
                sum((i - mean_x) ** 2 for i in range(n)) + 1e-6
        )

        # 将坡度映射为调整量
        adjustment = max(-1.0, min(1.0, slope * TREND_ALPHA * 5)) * TREND_WEIGHT * 10
        return max(0.0, min(10.0, raw_avg + adjustment))


# ====================== 图片单帧用（静态图片兼容）=======================
def calculate_single_focus(cls_name):
    """行为 → 基础专注度（图片用，不含时序/趋势）"""
    high = {"reading", "writing", "hand-raising"}
    low  = {"leaning over the table", "using phone"}
    if cls_name in high:
        return 8.5
    elif cls_name in {"bowing the head"}:
        return 5.0
    elif cls_name in low:
        return 1.0
    return 5.5


def get_class_focus_static(results):
    """静态图片专注度计算（兼容旧接口）"""
    total_num = len(results.boxes)
    if total_num == 0:
        return 0, 0.0
    sum_focus = sum(
        calculate_single_focus(Config.names[cid])
        for cid in results.boxes.cls.int().tolist()
    )
    return total_num, round(sum_focus / total_num, 1)


class DetectionApp(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setStyleSheet(LIGHT_STYLE)

        self._setup_ui()
        self._connect_signals()
        self._init_detection_resources()
        self.current_results = None

    def _setup_ui(self):
        self.display_width = 700
        self.display_height = 500
        self.source_path = None
        self.camera_active = False
        self.video_capture = None

        table = self.ui.tableWidget
        table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        table.verticalHeader().setDefaultSectionSize(40)
        table.setColumnWidth(0, 80)
        table.setColumnWidth(1, 200)
        table.setColumnWidth(2, 150)
        table.setColumnWidth(3, 90)
        table.setColumnWidth(4, 230)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)

    def _connect_signals(self):
        self.ui.PicBtn.clicked.connect(self._handle_image_input)
        self.ui.comboBox.activated.connect(self._update_selection)
        self.ui.VideoBtn.clicked.connect(self._handle_video_input)
        self.ui.CapBtn.clicked.connect(self._toggle_camera)
        self.ui.SaveBtn.clicked.connect(self._save_results)
        self.ui.ExitBtn.clicked.connect(QCoreApplication.quit)
        self.ui.FilesBtn.clicked.connect(self._process_image_batch)

    def _load_stylesheet(self):
        style_file = 'UIProgram/style.css'
        qss = QSSLoader.read_qss_file(style_file)
        self.setStyleSheet(qss)

    def _init_detection_resources(self):
        self.detector = YOLO('runs/detect/exp/weights/best.pt', task='detect')
        self.detector(np.zeros((48, 48, 3)))
        self.detection_font = ImageFont.truetype("Font/platech.ttf", 25, 0)
        self.color_palette = tools.Colors()
        self.frame_timer = QTimer()
        self.save_timer = QTimer()
        # 初始化视频流专注度追踪器
        self.focus_tracker = FocusTracker()

    # ====================== 切换显示全班/个人专注度 ======================
    def _update_selection(self):
        selection = self.ui.comboBox.currentText()

        if selection == '全部':
            display_img = self.current_result
            person_num, avg_focus = get_class_focus_static(self.current_results)
            self.ui.label_nums.setText(f"人数{person_num}|班级专注度{avg_focus}/10")
            self._show_detection_details(0)
        else:
            idx = int(selection.split('_')[-1])
            display_img = self.detector(self.source_path)[0][idx].plot()
            cls_id = self.detection_classes[idx]
            cls_name = Config.names[cls_id]
            single_focus = calculate_single_focus(cls_name)
            self.ui.label_nums.setText(f"单人专注度：{single_focus}/10")
            self._show_detection_details(idx)

        width, height = self._calculate_display_size(display_img)
        resized_img = cv2.resize(display_img, (width, height))
        qimage = tools.cvimg_to_qpiximg(resized_img)
        self.ui.label_show.setPixmap(qimage)
        self.ui.label_show.setAlignment(Qt.AlignCenter)

    # ====================== 功能函数 ======================
    def _handle_image_input(self):
        self._stop_video_capture()
        file_path, _ = QFileDialog.getOpenFileName(self, '选择图片', './', "图片文件 (*.jpg *.jpeg *.png)")
        if not file_path:
            return
        self._process_single_image(file_path)

    def _process_single_image(self, image_path):
        self.source_path = image_path
        self.ui.comboBox.setEnabled(True)

        start_time = time.time()
        detection_results = self.detector(image_path)[0]
        self.current_results = detection_results
        processing_time = time.time() - start_time

        boxes = detection_results.boxes.xyxy.tolist()
        self.detection_boxes = [list(map(int, box)) for box in boxes]
        self.detection_classes = detection_results.boxes.cls.int().tolist()
        confidences = detection_results.boxes.conf.tolist()
        self.confidence_scores = [f'{score * 100:.2f}%' for score in confidences]

        # 图片用静态算法
        person_num, avg_focus = get_class_focus_static(detection_results)

        self._update_detection_display(detection_results, processing_time)
        self._update_object_selection()
        self._show_detection_details()
        self._display_results_table(image_path)

        self.ui.label_nums.setText(f"人数 {person_num}|班级专注度{avg_focus}/10")

    def _update_detection_display(self, results, process_time):
        self.ui.time_lb.setText(f'{process_time:.3f} s')
        annotated_img = results.plot()
        self.current_result = annotated_img
        width, height = self._calculate_display_size(annotated_img)
        resized_img = cv2.resize(annotated_img, (width, height))
        qimage = tools.cvimg_to_qpiximg(resized_img)
        self.ui.label_show.setPixmap(qimage)
        self.ui.label_show.setAlignment(Qt.AlignCenter)
        self.ui.PiclineEdit.setText(self.source_path)

    def _calculate_display_size(self, image):
        h, w = image.shape[:2]
        ar = w / h
        if ar >= self.display_width / self.display_height:
            return self.display_width, int(self.display_width / ar)
        else:
            return int(self.display_height * ar), self.display_height

    def _update_object_selection(self):
        options = ['全部']
        for idx, cls_id in enumerate(self.detection_classes):
            options.append(f'{Config.names[cls_id]}_{idx}')
        self.ui.comboBox.clear()
        self.ui.comboBox.addItems(options)

    def _show_detection_details(self, index=0):
        if not self.detection_boxes:
            self._clear_detection_details()
            return
        box = self.detection_boxes[index]
        self.ui.type_lb.setText(Config.CH_names[self.detection_classes[index]])
        self.ui.label_conf.setText(self.confidence_scores[index])
        self.ui.label_xmin.setText(str(box[0]))
        self.ui.label_ymin.setText(str(box[1]))
        self.ui.label_xmax.setText(str(box[2]))
        self.ui.label_ymax.setText(str(box[3]))

    def _clear_detection_details(self):
        self.ui.type_lb.setText('')
        self.ui.label_conf.setText('')
        self.ui.label_xmin.setText('')
        self.ui.label_ymin.setText('')
        self.ui.label_xmax.setText('')
        self.ui.label_ymax.setText('')

    def _display_results_table(self, source_path):
        table = self.ui.tableWidget
        table.setRowCount(0)
        table.clearContents()
        self._append_results_table(source_path)

    def _append_results_table(self, source_path):
        """追加单张图片的检测结果到表格"""
        table = self.ui.tableWidget
        for idx, (box, cls_id, conf) in enumerate(
                zip(self.detection_boxes, self.detection_classes, self.confidence_scores)):
            row = table.rowCount()
            table.insertRow(row)
            items = [
                QTableWidgetItem(str(row + 1)),
                QTableWidgetItem(source_path),
                QTableWidgetItem(Config.CH_names[cls_id]),
                QTableWidgetItem(conf),
                QTableWidgetItem(str(box))
            ]
            for item in [items[0], items[2], items[3]]:
                item.setTextAlignment(Qt.AlignCenter)
            for col, item in enumerate(items):
                table.setItem(row, col, item)
        table.scrollToBottom()

    def _process_image_batch(self):
        self._stop_video_capture()
        folder = QFileDialog.getExistingDirectory(self, "选择图片文件夹", "./")
        if not folder:
            return
        self.source_path = folder

        # 清空表格准备批量显示
        table = self.ui.tableWidget
        table.setRowCount(0)
        table.clearContents()

        exts = {'jpg', 'png', 'jpeg', 'bmp'}
        image_files = [f for f in os.listdir(folder)
                      if os.path.isfile(os.path.join(folder, f)) and f.split('.')[-1].lower() in exts]

        # 禁用重绘直到所有处理完成
        table.setUpdatesEnabled(False)

        for f in sorted(image_files):
            p = os.path.join(folder, f)
            # 检测单张图片但不更新表格
            self._process_single_image_batch(p)
            QApplication.processEvents()

        # 处理完成后重新启用重绘
        table.setUpdatesEnabled(True)

        # 重要：保持 source_path 为文件夹路径，以便批量保存所有图片
        self.source_path = folder

    def _process_single_image_batch(self, image_path):
        """批量处理时使用的单张图片处理方法（不覆盖表格）"""
        self.source_path = image_path

        start_time = time.time()
        detection_results = self.detector(image_path)[0]
        self.current_results = detection_results
        processing_time = time.time() - start_time

        boxes = detection_results.boxes.xyxy.tolist()
        self.detection_boxes = [list(map(int, box)) for box in boxes]
        self.detection_classes = detection_results.boxes.cls.int().tolist()
        confidences = detection_results.boxes.conf.tolist()
        self.confidence_scores = [f'{score * 100:.2f}%' for score in confidences]

        # 只更新最后一张图片的显示
        self._update_detection_display(detection_results, processing_time)
        self._update_object_selection()
        self._show_detection_details()

        # 追加到表格，不清空
        self._append_results_table(image_path)

        person_num, avg_focus = get_class_focus_static(detection_results)
        self.ui.label_nums.setText(f"已处理: {image_path.split('/')[-1]} | 专注度{avg_focus}/10")

    def _handle_video_input(self):
        if self.camera_active:
            self._toggle_camera()
        path = self._get_video_path()
        if path:
            self._start_video_processing(path)
            self.ui.comboBox.setEnabled(False)

    def _get_video_path(self):
        path, _ = QFileDialog.getOpenFileName(self, '选择视频', './', "视频文件 (*.avi *.mp4)")
        if path:
            self.source_path = path
            self.ui.VideolineEdit.setText(path)
        return path

    def _start_video_processing(self, vp):
        self.video_capture = cv2.VideoCapture(vp)
        # 重置追踪器
        self.focus_tracker = FocusTracker()
        # 初始化专注度记录
        self.focus_history = []  # 存储每秒的专注度
        self.frame_count = 0     # 帧计数
        fps = self.video_capture.get(cv2.CAP_PROP_FPS) if vp != 0 else 30  # 摄像头默认30fps
        self.frames_per_second = int(fps)
        self.frame_timer.start(1)
        self.frame_timer.timeout.connect(self._process_video_frame)

    def _stop_video_capture(self):
        if self.video_capture:
            self.video_capture.release()
            self.frame_timer.stop()
            self.camera_active = False
            self.ui.CaplineEdit.setText('摄像头未开启')
            self.video_capture = None

    def _process_video_frame(self):
        ret, frame = self.video_capture.read()
        if not ret:
            # 视频结束时，计算并显示整个视频的平均专注度
            if hasattr(self, 'focus_history') and len(self.focus_history) > 0:
                overall_avg = sum(self.focus_history) / len(self.focus_history)
                QMessageBox.information(
                    self, '视频分析完成',
                    f'视频时长: {len(self.focus_history)}秒\n'
                    f'全班平均专注度: {overall_avg:.2f}/10'
                )
            self._stop_video_capture()
            return
        st = time.time()
        res = self.detector(frame)[0]
        self.current_results = res
        pt = time.time() - st

        boxes = res.boxes.xyxy.int().tolist()
        classes = res.boxes.cls.int().tolist()
        confidences = res.boxes.conf.tolist()

        self.detection_boxes = boxes
        self.detection_classes = classes
        self.confidence_scores = [f'{c * 100:.2f}%' for c in confidences]

        # 使用增强版追踪器（包含时序+趋势）
        num, avg = self.focus_tracker.compute(boxes, classes, confidences)
        self.ui.label_nums.setText(f"人数 {num}|班级专注度{avg}/10")

        # 每秒记录一次专注度
        if hasattr(self, 'frame_count') and hasattr(self, 'frames_per_second'):
            self.frame_count += 1
            if self.frame_count % self.frames_per_second == 0:
                self.focus_history.append(avg)

        self._update_detection_display(res, pt)
        self._update_object_selection()
        self._show_detection_details()
        self._display_results_table(self.source_path)

    def _toggle_camera(self):
        self.camera_active = not self.camera_active
        if self.camera_active:
            self.ui.CaplineEdit.setText('摄像头开启')
            self.video_capture = cv2.VideoCapture(0)
            # 重置追踪器
            self.focus_tracker = FocusTracker()
            # 初始化专注度记录
            self.focus_history = []
            self.frame_count = 0
            self.frames_per_second = 30
            self._start_video_processing(0)
            self.ui.comboBox.setEnabled(False)
        else:
            self.ui.CaplineEdit.setText('摄像头未开启')
            self.ui.label_show.clear()
            self._stop_video_capture()

    def _save_results(self):
        if not self.video_capture and not self.source_path:
            QMessageBox.information(self, '提示', '请先打开图片或视频')
            return
        if self.camera_active:
            QMessageBox.information(self, '提示', '无法保存实时摄像头')
            return
        if self.video_capture:
            self._save_video_result()
        else:
            self._save_image_result()

    def _save_video_result(self):
        c = QMessageBox.question(self, '确认', '保存视频耗时较长，确定吗？')
        if c == QMessageBox.No: return
        self._stop_video_capture()
        s = VideoSaverThread(self.source_path, self.detector, self.ui.comboBox.currentText())
        s.start()
        s.update_ui_signal.connect(self._update_progress)

    def _save_image_result(self):
        if os.path.isfile(self.source_path):
            try:
                name, ext = os.path.basename(self.source_path).rsplit('.', 1)
                sp = os.path.join(Config.save_path, f'{name}_result.{ext}')

                # 计算专注度（单张图片使用 current_results）
                person_num, avg_focus = get_class_focus_static(self.current_results)

                # 在图片上添加专注度信息
                result_img_with_focus = tools.cv2AddChineseText(
                    self.current_result,
                    f"班级专注度: {avg_focus}/10  人数: {person_num}",
                    (10, 30),
                    textColor=(0, 255, 0), textSize=30
                )

                cv2.imwrite(sp, result_img_with_focus)
                QMessageBox.information(self, '完成', f'已保存：{sp}\n班级专注度: {avg_focus}/10  人数: {person_num}')
            except Exception as e:
                QMessageBox.warning(self, '保存失败', f'保存失败：{str(e)}\n\n请检查 D: 盘是否存在或是否有写入权限')
        else:
            exts = {'jpg', 'png', 'jpeg', 'bmp'}
            saved_count = 0
            failed_count = 0
            failed_files = []
            all_files = os.listdir(self.source_path)

            for f in sorted(all_files):
                if f.split('.')[-1].lower() in exts:
                    try:
                        p = os.path.join(self.source_path, f)
                        n, e = f.rsplit('.', 1)
                        save_path = os.path.join(Config.save_path, f'{n}_result.{e}')

                        # 检测图片
                        detection_results = self.detector(p)[0]
                        result_img = detection_results.plot()

                        # 计算专注度
                        person_num, avg_focus = get_class_focus_static(detection_results)

                        # 在图片左上角添加专注度信息
                        focus_text = f"班级专注度: {avg_focus}/10  人数: {person_num}"
                        result_img = tools.cv2AddChineseText(result_img, focus_text, (10, 30),
                                                             textColor=(0, 255, 0), textSize=30)

                        # 写入文件
                        success = cv2.imwrite(save_path, result_img)
                        if success:
                            saved_count += 1
                            print(f'[保存成功] {f} -> {save_path}')
                        else:
                            failed_count += 1
                            failed_files.append(f'{f}: cv2.imwrite 返回 False')
                            print(f'[保存失败] {f} -> cv2.imwrite 返回 False')

                    except Exception as e:
                        failed_count += 1
                        failed_files.append(f'{f}: {str(e)}')
                        print(f'[保存异常] {f}: {str(e)}')

            print(f'\n===== 保存统计 =====')
            print(f'文件夹中图片总数: {len(all_files)}')
            print(f'匹配的图片文件: {len([f for f in all_files if f.split(".")[-1].lower() in exts])}')
            print(f'成功保存: {saved_count}')
            print(f'保存失败: {failed_count}')
            print(f'保存位置: {Config.save_path}')
            print('=' * 20)

            if failed_count > 0:
                QMessageBox.warning(self, '部分保存失败',
                    f'批量保存完成\n成功: {saved_count} 张\n失败: {failed_count} 张\n\n'
                    f'失败文件:\n' + '\n'.join(failed_files[:10]))
            else:
                QMessageBox.information(self, '完成', f'批量保存完成\n成功: {saved_count} 张\n保存位置: {Config.save_path}')

    def _update_progress(self, c, t):
        if c == 1:
            self.pd = ProgressBar(self)
            self.pd.show()
        if c >= t:
            self.pd.close()
            QMessageBox.information(self, '完成', '视频保存完成')
            return
        self.pd.setValue(c, t, int(c / t * 100))
        QApplication.processEvents()


class VideoSaverThread(QThread):
    update_ui_signal = pyqtSignal(int, int)

    def __init__(self, vp, m, sel):
        super().__init__()
        self.vp = vp
        self.m = m
        self.a = True

    def run(self):
        cap = cv2.VideoCapture(self.vp)
        fps = cap.get(cv2.CAP_PROP_FPS)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        wtr = cv2.VideoWriter(os.path.join(Config.save_path, 'result.avi'), cv2.VideoWriter_fourcc(*'XVID'), fps,
                              (w, h))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        i = 0
        while cap.isOpened() and self.a:
            i += 1
            ret, f = cap.read()
            if not ret: break
            wtr.write(self.m(f)[0].plot())
            self.update_ui_signal.emit(i, total)
        cap.release()
        wtr.release()

    def stop(self):
        self.a = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DetectionApp()
    win.show()
    sys.exit(app.exec_())
