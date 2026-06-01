# -*- coding: utf-8 -*-
"""Train the strongest practical YOLOv8m variant for this classroom dataset.

Strategy:
- Start from the best 640px YOLOv8m baseline if it exists.
- Fine-tune at 800px to improve small/medium classroom behavior targets.
- Use the tail-oversampled training split to reduce long-tail class bias.
- Keep augmentation weak because classroom behavior labels depend on posture context.
"""

from pathlib import Path

import torch
import yaml

from ultralytics.nn.tasks import DetectionModel

# PyTorch 2.6 compatibility for loading Ultralytics checkpoints.
torch.serialization.add_safe_globals([DetectionModel])
_original_load = torch.load
torch.load = lambda *args, **kwargs: _original_load(*args, **kwargs, weights_only=False)

from ultralytics import YOLO


BASELINE_WEIGHTS = Path("runs/detect/baseline_mAP_100epochs/weights/best.pt")
FALLBACK_WEIGHTS = Path("yolov8m.pt")
DATASET_DIR = Path("datasets/classroom_tail_oversampled")
TEMP_DATA_YAML = Path("datasets/data_strong_img800_tail_abs.yaml")
RUN_NAME = "strong_img800_tail_weakaug"

CLASS_NAMES = [
    "hand-raising",
    "reading",
    "writing",
    "using phone",
    "bowing the head",
    "leaning over the table",
]


def select_start_weights() -> str:
    """Prefer the trained baseline; fall back to COCO-pretrained YOLOv8m."""
    if BASELINE_WEIGHTS.exists():
        return BASELINE_WEIGHTS.as_posix()
    if FALLBACK_WEIGHTS.exists():
        print(f"Warning: {BASELINE_WEIGHTS} not found, using {FALLBACK_WEIGHTS}.")
        return FALLBACK_WEIGHTS.as_posix()
    raise FileNotFoundError(
        f"Neither {BASELINE_WEIGHTS} nor {FALLBACK_WEIGHTS} exists."
    )


def build_abs_data_yaml() -> str:
    """Write an absolute-path yaml to avoid path encoding issues on Windows."""
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
    TEMP_DATA_YAML.parent.mkdir(parents=True, exist_ok=True)
    with TEMP_DATA_YAML.open("w", encoding="utf-8", newline="\n") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    return TEMP_DATA_YAML.as_posix()


if __name__ == "__main__":
    weights = select_start_weights()
    data_yaml = build_abs_data_yaml()
    model = YOLO(weights)

    print("=" * 70)
    print("Strong YOLOv8m fine-tuning: imgsz=800 + tail balance + weak aug")
    print(f"Start weights: {weights}")
    print(f"Data yaml:     {data_yaml}")
    print(f"Run name:      {RUN_NAME}")
    print("=" * 70)

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
        hsv_s=0.30,
        hsv_v=0.30,
        degrees=3.0,
        translate=0.05,
        scale=0.15,
        shear=1.0,
        perspective=0.0,
        flipud=0.0,
        fliplr=0.5,
        mosaic=0.0,
        mixup=0.0,
        copy_paste=0.0,
        close_mosaic=0,
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

    print("=" * 70)
    print("Training complete")
    print(f"Best model:  runs/detect/{RUN_NAME}/weights/best.pt")
    print(f"Metrics CSV: runs/detect/{RUN_NAME}/results.csv")
    print("=" * 70)
