# -*- coding: utf-8 -*-
"""Train YOLOv8m with CoordAtt in Backbone and ECA in Neck."""

import torch

from ultralytics.nn.tasks import DetectionModel

# PyTorch 2.6 compatibility for loading Ultralytics checkpoints.
torch.serialization.add_safe_globals([DetectionModel])
_original_load = torch.load
def _patched_load(*args, **kwargs):
    if "weights_only" not in kwargs:
        kwargs["weights_only"] = False
    return _original_load(*args, **kwargs)
torch.load = _patched_load

from ultralytics import YOLO


MODEL_CFG = "ultralytics/cfg/models/v8/yolov8m-coordatt-backbone-eca-neck.yaml"
PRETRAINED_WEIGHTS = "yolov8m.pt"
DATA_YAML = "datasets/data.yaml"
RUN_NAME = "coordatt_backbone_eca_neck_v2"


if __name__ == "__main__":
    # Ultralytics built-in load(): 按名称+形状自动匹配，比手动 layer_map 更完整
    model = YOLO(MODEL_CFG).load(PRETRAINED_WEIGHTS)

    print("=" * 60)
    print("YOLOv8m + CoordAtt Backbone + ECA Neck training")
    print(f"Config: {MODEL_CFG}")
    print(f"Pretrained weights: {PRETRAINED_WEIGHTS} (auto shape-matching)")
    print(f"Run name: {RUN_NAME}")
    print("=" * 60)

    results = model.train(
        data=DATA_YAML,
        epochs=60,
        patience=20,
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
        # 弱增强：课堂行为依赖空间语义，强增强会破坏 CoordAtt 依赖的 X/Y 位置信息
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
        mosaic=0.0,         # CoordAtt 依赖空间位置 → 必须关闭 mosaic
        mixup=0.0,
        copy_paste=0.0,
        close_mosaic=0,
        amp=True,
        cache=True,
        box=7.5,
        cls=0.5,
        dfl=1.5,
        freeze=0,           # CoordAtt 在 model.5/8，绝不能用 freeze=10
        pretrained=False,
        verbose=True,
        seed=42,
        exist_ok=False,
    )

    print("=" * 60)
    print("CoordAtt Backbone + ECA Neck training complete")
    print(f"Best model: runs/detect/{RUN_NAME}/weights/best.pt")
    print("=" * 60)
