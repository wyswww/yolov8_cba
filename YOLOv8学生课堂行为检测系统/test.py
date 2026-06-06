# -*- coding: utf-8 -*-
"""Validate six trained YOLO models on the test split and print a comparison table."""

import os
import warnings

import torch

warnings.filterwarnings("ignore")

# PyTorch 2.6 compatibility for loading Ultralytics checkpoints.
_original_load = torch.load
torch.load = lambda *args, **kwargs: _original_load(*args, **kwargs, weights_only=False)

from ultralytics import YOLO


MODELS = [
    {"name": "1_baseline_mAP_100epochs",          "path": "runs/detect/baseline_mAP_100epochs/weights/best.pt",              "imgsz": 640},
    {"name": "2_optimized_attention",              "path": "runs/detect/optimized_attention_light_m_pretrained/weights/best.pt", "imgsz": 640},
    {"name": "3_yolov8m_p2",                       "path": "runs/detect/yolov8m_p2_100epochs/weights/best.pt",                 "imgsz": 640},
    {"name": "4_baseline_finetune_img800_weakaug", "path": "runs/detect/baseline_finetune_img800_weakaug/weights/best.pt",    "imgsz": 800},
    {"name": "5_coordatt_backbone_eca_neck",       "path": "runs/detect/coordatt_backbone_eca_neck_m_pretrained/weights/best.pt", "imgsz": 640},
    {"name": "6_strong_img800_tail_weakaug",       "path": "runs/detect/strong_img800_tail_weakaug/weights/best.pt",          "imgsz": 800},
    {"name": "7_exp", "path": "runs/detect/exp/weights/best.pt",  "imgsz": 640},
]

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
        print(f"Skip missing model: {model_path}")
        return None

    print(f"Testing: {model_name}")
    print(f"Model path: {model_path}")
    print(f"imgsz: {imgsz}")

    try:
        model = YOLO(model_path)
        config = BASE_TEST_CONFIG.copy()
        config["imgsz"] = imgsz
        config["name"] = f"test_{model_name}"
        metrics = model.val(**config)

        print("\nResults:")
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
        print("\nPer-class mAP@0.5:")
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
        print(f"Validation failed: {exc}")
        return None


def compare_results(results):
    valid_results = {name: res for name, res in results.items() if res}
    if not valid_results:
        print("\nNo valid results to compare.")
        return

    print("\n" + "=" * 86)
    print("六种模型 - 测试集指标对比")
    print("=" * 86)
    print(f"{'模型':<44} {'Prec':<10} {'Rec':<10} {'mAP@0.5':<10} {'mAP@0.5:0.95':<14}")
    print("-" * 88)

    baseline_res = None
    for name, res in valid_results.items():
        print(
            f"{name:<44} {res['precision']:<10.4f} {res['recall']:<10.4f} "
            f"{res['map50']:<10.4f} {res['map50_95']:<14.4f}"
        )
        if "baseline_mAP_100epochs" in name:
            baseline_res = res

    if baseline_res is None:
        return

    print("\n相较基线 mAP@0.5 变化:")
    for name, res in valid_results.items():
        if "baseline_mAP_100epochs" in name:
            continue
        improvement = res["map50"] - baseline_res["map50"]
        percent = improvement / baseline_res["map50"] * 100
        print(f"  {name}: {improvement:+.4f} ({percent:+.2f}%)")


def main():
    print("=" * 60)
    print("YOLOv8 六种模型验证 (测试集)")
    print("=" * 60)

    results = {}
    for m in MODELS:
        result = test_model(m["name"], m["path"], m["imgsz"])
        if result:
            results[m["name"]] = result

    compare_results(results)
    print("\n测试完成！")


if __name__ == "__main__":
    main()
