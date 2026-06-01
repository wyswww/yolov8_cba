# -*- coding: utf-8 -*-
"""Train YOLOv8m at higher resolution with classroom-friendly weak augmentation."""

import torch

from ultralytics.nn.tasks import DetectionModel

# PyTorch 2.6 compatibility for loading Ultralytics checkpoints.
torch.serialization.add_safe_globals([DetectionModel])
_original_load = torch.load
torch.load = lambda *args, **kwargs: _original_load(*args, **kwargs, weights_only=False)

from ultralytics import YOLO


MODEL_WEIGHTS = "yolov8m.pt"
DATA_YAML = "datasets/data.yaml"
RUN_NAME = "yolov8m_img800_weakaug_120epochs"


if __name__ == "__main__":
    model = YOLO(MODEL_WEIGHTS)

    print("=" * 60)
    print("YOLOv8m imgsz=800 weak-augmentation training")
    print(f"Pretrained weights: {MODEL_WEIGHTS}")
    print(f"Run name: {RUN_NAME}")
    print("=" * 60)

    results = model.train(
        data=DATA_YAML,
        epochs=120,
        patience=40,
        batch=4,
        imgsz=800,
        device="0",
        workers=0,
        project="runs/detect",
        name=RUN_NAME,
        optimizer="AdamW",
        lr0=0.0004,
        lrf=0.02,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=4.0,
        warmup_momentum=0.8,
        warmup_bias_lr=0.05,
        cos_lr=True,
        hsv_h=0.01,
        hsv_s=0.35,
        hsv_v=0.3,
        degrees=3.0,
        translate=0.06,
        scale=0.2,
        shear=1.0,
        perspective=0.0001,
        flipud=0.0,
        fliplr=0.5,
        mosaic=0.35,
        mixup=0.0,
        copy_paste=0.0,
        close_mosaic=20,
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
    print("Training complete")
    print(f"Best model: runs/detect/{RUN_NAME}/weights/best.pt")
    print("=" * 60)
