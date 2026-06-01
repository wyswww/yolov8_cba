# -*- coding: utf-8 -*-
"""
Train YOLOv8 with the optimized lightweight-attention architecture.

Key points for a fair comparison with the baseline:
1. The YAML sets scale: m, matching yolov8m.pt.
2. Only lightweight ECA attention is inserted at P3/P4.
3. The model explicitly loads matching yolov8m.pt layers.
"""

import torch

from ultralytics.nn.tasks import DetectionModel

# PyTorch 2.6 compatibility for loading Ultralytics checkpoints.
torch.serialization.add_safe_globals([DetectionModel])
_original_load = torch.load
torch.load = lambda *args, **kwargs: _original_load(*args, **kwargs, weights_only=False)

from ultralytics import YOLO


MODEL_CFG = "ultralytics/cfg/models/v8/yolov8m-optimized-attention.yaml"
PRETRAINED_WEIGHTS = "yolov8m.pt"
DATA_YAML = "datasets/data.yaml"
RUN_NAME = "optimized_attention_light_m_pretrained"


def load_yolov8m_weights_by_layer_mapping(model: YOLO, weights_path: str) -> int:
    """Load YOLOv8m weights into the attention model after layer insertions."""
    source_model = YOLO(weights_path).model
    source_state = source_model.float().state_dict()
    target_state = model.model.state_dict()

    # Original YOLOv8m layer index -> lightweight-attention layer index.
    layer_map = {
        0: 0,
        1: 1,
        2: 2,
        3: 3,
        4: 4,
        5: 6,
        6: 7,
        7: 9,
        8: 10,
        9: 11,
        12: 14,
        15: 17,
        16: 18,
        18: 20,
        19: 21,
        21: 23,
        22: 24,
    }

    transfer_state = {}
    for source_idx, target_idx in layer_map.items():
        source_prefix = f"model.{source_idx}."
        target_prefix = f"model.{target_idx}."
        for key, value in source_state.items():
            if not key.startswith(source_prefix):
                continue
            target_key = key.replace(source_prefix, target_prefix, 1)
            if target_key in target_state and target_state[target_key].shape == value.shape:
                transfer_state[target_key] = value

    model.model.load_state_dict(transfer_state, strict=False)
    return len(transfer_state)


if __name__ == "__main__":
    model = YOLO(MODEL_CFG)
    transferred = load_yolov8m_weights_by_layer_mapping(model, PRETRAINED_WEIGHTS)

    print("=" * 60)
    print("YOLOv8m + lightweight ECA attention training")
    print(f"Config: {MODEL_CFG}")
    print(f"Pretrained weights: {PRETRAINED_WEIGHTS}")
    print(f"Transferred weights: {transferred}/{len(model.model.state_dict())}")
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
        pretrained=False,
        verbose=True,
        seed=42,
        exist_ok=False,
    )

    print("=" * 60)
    print("Training complete")
    print(f"Best model: runs/detect/{RUN_NAME}/weights/best.pt")
    print("=" * 60)
