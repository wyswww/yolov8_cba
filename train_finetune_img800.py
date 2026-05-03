# -*- coding: utf-8 -*-
"""Fine-tune the strong YOLOv8m baseline at higher resolution with weak augmentation."""

import torch

from ultralytics.nn.tasks import DetectionModel

# PyTorch 2.6 compatibility for loading Ultralytics checkpoints.
torch.serialization.add_safe_globals([DetectionModel])
_original_load = torch.load
torch.load = lambda *args, **kwargs: _original_load(*args, **kwargs, weights_only=False)

from ultralytics import YOLO


MODEL_WEIGHTS = "runs/detect/baseline_mAP_100epochs/weights/best.pt"
DATA_YAML = "datasets/data.yaml"
RUN_NAME = "baseline_finetune_img800_weakaug"


if __name__ == "__main__":
    model = YOLO(MODEL_WEIGHTS)

    print("=" * 60)
    print("YOLOv8m baseline fine-tuning at imgsz=800")
    print(f"Start weights: {MODEL_WEIGHTS}")
    print(f"Run name: {RUN_NAME}")
    print("=" * 60)

    results = model.train(
        data=DATA_YAML,
        epochs=50,
        patience=20,
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
        hsv_s=0.3,
        hsv_v=0.3,
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

    print("=" * 60)
    print("Fine-tuning complete")
    print(f"Best model: runs/detect/{RUN_NAME}/weights/best.pt")
    print("=" * 60)
