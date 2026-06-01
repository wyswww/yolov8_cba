# -*- coding: utf-8 -*-
"""
Train the 100-epoch YOLOv8m baseline for classroom behavior detection.

This run is the reference baseline for the optimized-attention model:
- Same dataset
- Same YOLOv8m scale
- Same image size and batch size
- Same optimizer and augmentation settings as the attention run
- No custom attention modules
"""

import torch

from ultralytics.nn.tasks import DetectionModel

# PyTorch 2.6 compatibility for loading Ultralytics checkpoints.
torch.serialization.add_safe_globals([DetectionModel])
_original_load = torch.load
torch.load = lambda *args, **kwargs: _original_load(*args, **kwargs, weights_only=False)

from ultralytics import YOLO


MODEL_WEIGHTS = "yolov8m.pt"
DATA_YAML = "datasets/data_tail_oversampled.yaml"
RUN_NAME = "baseline_mAP_100epochs"


if __name__ == "__main__":
    model = YOLO(MODEL_WEIGHTS)

    print("=" * 60)
    print("YOLOv8m 100-epoch baseline training")
    print(f"Pretrained weights: {MODEL_WEIGHTS}")
    print(f"Run name: {RUN_NAME}")
    print("=" * 60)

    results = model.train(
        data=DATA_YAML,
        epochs=100,
        patience=30,
        batch=8,
        imgsz=640,
        device="0",
        workers=0,
        project="runs/detect",
        name=RUN_NAME,
        optimizer="AdamW",
        lr0=0.0005,
        lrf=0.01,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=5.0,
        warmup_momentum=0.8,
        warmup_bias_lr=0.1,
        hsv_h=0.015,
        hsv_s=0.5,
        hsv_v=0.4,
        degrees=5.0,
        translate=0.1,
        scale=0.3,
        shear=2.0,
        perspective=0.0002,
        flipud=0.0,
        fliplr=0.5,
        mosaic=0.8,
        mixup=0.1,
        copy_paste=0.05,
        close_mosaic=10,
        amp=True,
        cache=True,
        box=7.5,
        cls=0.5,
        dfl=1.5,
        pretrained=True,
        verbose=True,
        seed=42,
        exist_ok=False,
    )

    print("=" * 60)
    print("Baseline training complete")
    print(f"Best model: runs/detect/{RUN_NAME}/weights/best.pt")
    print(f"Metrics CSV: runs/detect/{RUN_NAME}/results.csv")
    print("=" * 60)
