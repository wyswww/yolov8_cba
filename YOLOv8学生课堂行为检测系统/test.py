# -*- coding: utf-8 -*-
"""Validate trained YOLO models on the test split and print a comparison table."""

import os
import warnings

import torch

warnings.filterwarnings("ignore")

# PyTorch 2.6 compatibility for loading Ultralytics checkpoints.
_original_load = torch.load
torch.load = lambda *args, **kwargs: _original_load(*args, **kwargs, weights_only=False)

from ultralytics import YOLO


MODELS = {
    "baseline_mAP_100epochs": "runs/detect/baseline_mAP_100epochs/weights/best.pt",

    "optimized_attention_light_m_pretrained": "runs/detect/optimized_attention_light_m_pretrained/weights/best.pt",
    "yolov8m_p2_100epochs": "runs/detect/yolov8m_p2_100epochs/weights/best.pt",
    "baseline_finetune_img800_weakaug": "runs/detect/baseline_finetune_img800_weakaug/weights/best.pt",
    "baseline_finetune_img800_weakaug2": "runs/detect/baseline_finetune_img800_weakaug2/weights/best.pt",
    "yolov8m_img800_weakaug_120epochs": "runs/detect/yolov8m_img800_weakaug_120epochs/weights/best.pt",
}

TEST_CONFIG = {
    "data": "datasets/data.yaml",
    "split": "test",
    "imgsz": 640,
    "batch": 8,
    "workers": 0,
    "conf": 0.001,
    "iou": 0.6,
    "plots": True,
    "save_json": True,
    "project": "runs/detect",
    "exist_ok": True,
}


def test_model(model_name, model_path):
    print("\n" + "=" * 60)

    if not os.path.exists(model_path):
        print(f"Skip missing model: {model_path}")
        return None

    print(f"Testing: {model_name}")
    print(f"Model path: {model_path}")

    try:
        model = YOLO(model_path)
        config = TEST_CONFIG.copy()
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
        for i, (name, ap) in enumerate(zip(class_names, metrics.box.ap50), start=1):
            bar = "#" * int(ap * 20)
            print(f"  {i}. {name:<24} {ap:.4f} {bar}")

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
    if len(valid_results) < 2:
        return

    print("\n" + "=" * 60)
    print("Model comparison")
    print("=" * 60)
    print(f"{'Model':<42} {'mAP@0.5':<10} {'mAP@0.5:0.95':<14} {'Prec':<10} {'Rec':<10}")
    print("-" * 90)

    baseline_map50 = None
    for name, res in valid_results.items():
        print(
            f"{name:<42} {res['map50']:<10.4f} {res['map50_95']:<14.4f} "
            f"{res['precision']:<10.4f} {res['recall']:<10.4f}"
        )
        if name == "baseline_mAP_100epochs":
            baseline_map50 = res["map50"]

    if baseline_map50 is None:
        return

    print("\nCompared with baseline mAP@0.5:")
    for name, res in valid_results.items():
        if name == "baseline_mAP_100epochs":
            continue
        improvement = res["map50"] - baseline_map50
        percent = improvement / baseline_map50 * 100
        print(f"  {name}: {improvement:+.4f} ({percent:+.2f}%)")


def main():
    print("=" * 60)
    print("YOLOv8 model validation")
    print("=" * 60)

    results = {}
    for model_name, model_path in MODELS.items():
        result = test_model(model_name, model_path)
        if result:
            results[model_name] = result

    compare_results(results)


if __name__ == "__main__":
    main()
