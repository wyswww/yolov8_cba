# -*- coding: utf-8 -*-
"""Fine-tune the best baseline at imgsz=800 on the tail-oversampled dataset."""

from pathlib import Path

import torch
import yaml

from ultralytics.nn.tasks import DetectionModel

# PyTorch 2.6 compatibility for loading Ultralytics checkpoints.
torch.serialization.add_safe_globals([DetectionModel])
_original_load = torch.load
torch.load = lambda *args, **kwargs: _original_load(*args, **kwargs, weights_only=False)

from ultralytics import YOLO


MODEL_WEIGHTS = "runs/detect/baseline_mAP_100epochs/weights/best.pt"
FALLBACK_WEIGHTS = "yolov8m.pt"
RUN_NAME = "baseline_img800_balanced_finetune"
DATASET_DIR = Path("datasets") / "classroom_tail_oversampled"
TEMP_DATA_YAML = Path("datasets") / "data_tail_oversampled_abs.yaml"

CLASS_NAMES = [
    "hand-raising",
    "reading",
    "writing",
    "using phone",
    "bowing the head",
    "leaning over the table",
]


def build_data_yaml() -> str:
    """Write an absolute-path dataset yaml to avoid Chinese path encoding issues."""
    dataset_root = DATASET_DIR.resolve()
    if not dataset_root.exists():
        raise FileNotFoundError(
            f"{dataset_root} does not exist. Run oversample_tail_classes.py first."
        )

    data = {
        "path": dataset_root.as_posix(),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "nc": len(CLASS_NAMES),
        "names": CLASS_NAMES,
    }
    with TEMP_DATA_YAML.open("w", encoding="utf-8", newline="\n") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    return TEMP_DATA_YAML.as_posix()


def select_weights() -> str:
    if Path(MODEL_WEIGHTS).exists():
        return MODEL_WEIGHTS
    print(f"Warning: {MODEL_WEIGHTS} not found, falling back to {FALLBACK_WEIGHTS}")
    return FALLBACK_WEIGHTS


if __name__ == "__main__":
    data_yaml = build_data_yaml()
    weights = select_weights()
    model = YOLO(weights)

    print("=" * 60)
    print("YOLOv8m baseline fine-tuning: imgsz=800 + tail-balanced dataset")
    print(f"Start weights: {weights}")
    print(f"Data: {data_yaml}")
    print(f"Run name: {RUN_NAME}")
    print("=" * 60)

    results = model.train(
        data=data_yaml,
        epochs=60,
        patience=25,
        batch=4,
        imgsz=800,
        device="0",
        workers=0,
        project="runs/detect",
        name=RUN_NAME,
        optimizer="AdamW",
        lr0=0.0001,
        lrf=0.05,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=2.0,
        warmup_momentum=0.8,
        warmup_bias_lr=0.01,
        cos_lr=True,
        hsv_h=0.01,
        hsv_s=0.35,
        hsv_v=0.30,
        degrees=2.0,
        translate=0.05,
        scale=0.18,
        shear=0.5,
        perspective=0.0,
        flipud=0.0,
        fliplr=0.5,
        mosaic=0.20,
        mixup=0.0,
        copy_paste=0.0,
        close_mosaic=15,
        amp=True,
        cache=True,
        box=7.5,
        cls=0.65,
        dfl=1.5,
        pretrained=True,
        verbose=True,
        seed=42,
        exist_ok=False,
    )

    print("=" * 60)
    print("Fine-tuning complete")
    print(f"Best model: runs/detect/{RUN_NAME}/weights/best.pt")
    print(f"Metrics CSV: runs/detect/{RUN_NAME}/results.csv")
    print("=" * 60)
