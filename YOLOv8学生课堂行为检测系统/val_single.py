# -*- coding: utf-8 -*-
"""Validate single trained YOLO model on the test split."""

import os
import warnings

import torch

warnings.filterwarnings("ignore")

# PyTorch 2.6 加载权重兼容补丁
_original_load = torch.load
def _patched_load(*args, **kwargs):
    kwargs.setdefault('weights_only', False)
    return _original_load(*args, **kwargs)
torch.load = _patched_load

from ultralytics import YOLO

# ========== 修改下面三行即可切换模型 ==========
MODEL_NAME = "coordatt_backbone_eca_neck_m_pretrained"
# best.pt = 验证集最优  last.pt = 最新（训练中测这个才能看到变化）
MODEL_PATH = "runs/detect/coordatt_backbone_eca_neck_v2/weights/best.pt"
IMGSZ = 640
# ==============================================

BASE_TEST_CONFIG = {
    "data": "datasets/data.yaml",
    "split": "test",
    "batch": 8,
    "workers": 0,
    "conf": 0.001,
    "iou": 0.6,
    "plots": True,
    "save_json": True,
    "project": "runs/detect",
    "exist_ok": True,
}


def test_model(model_name, model_path, imgsz):
    print("\n" + "=" * 60)

    if not os.path.exists(model_path):
        print(f"模型文件不存在: {model_path}")
        return None

    print(f"正在测试模型: {model_name}")
    print(f"权重路径: {model_path}")
    print(f"输入尺寸 imgsz: {imgsz}")

    try:
        model = YOLO(model_path)
        config = BASE_TEST_CONFIG.copy()
        config["imgsz"] = imgsz
        config["name"] = f"test_{model_name}"
        metrics = model.val(**config)

        print("\n整体评估指标：")
        print(f"  Precision:     {metrics.box.mp:.4f}")
        print(f"  Recall:        {metrics.box.mr:.4f}")
        print(f"  mAP@0.5:       {metrics.box.map50:.4f}")
        print(f"  mAP@0.5:0.95:  {metrics.box.map:.4f}")

        class_names = [
            "hand-raising",
            "reading",
            "writing",
            "using phone",
            "bowing the head",
            "leaning over the table",
        ]
        print("\n每一类 mAP@0.5 详情：")
        for i, (cls_name, ap) in enumerate(zip(class_names, metrics.box.ap50), start=1):
            bar = "#" * int(ap * 20)
            print(f"  {i}. {cls_name:<24} {ap:.4f} {bar}")

        return {
            "precision": metrics.box.mp,
            "recall": metrics.box.mr,
            "map50": metrics.box.map50,
            "map50_95": metrics.box.map,
        }
    except Exception as exc:
        print(f"验证失败: {exc}")
        return None


def main():
    print("=" * 60)
    print("YOLOv8 单模型测试集验证程序")
    print("=" * 60)

    res = test_model(MODEL_NAME, MODEL_PATH, IMGSZ)
    if res:
        print("\n===== 指标汇总 =====")
        print(f"精确率(Precision): {res['precision']:.4f}")
        print(f"召回率(Recall):    {res['recall']:.4f}")
        print(f"mAP@0.5:            {res['map50']:.4f}")
        print(f"mAP@0.5:0.95:       {res['map50_95']:.4f}")

    print("\n测试运行结束！")


if __name__ == "__main__":
    main()