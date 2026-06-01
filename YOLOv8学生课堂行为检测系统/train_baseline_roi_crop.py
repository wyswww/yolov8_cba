# -*- coding: utf-8 -*-
"""Train YOLOv8m on the ROI-cropped classroom dataset."""

import random
import tempfile
from pathlib import Path

import torch
import yaml

from ultralytics.nn.tasks import DetectionModel

# PyTorch 2.6 compatibility for loading Ultralytics checkpoints.
torch.serialization.add_safe_globals([DetectionModel])
_original_load = torch.load
torch.load = lambda *args, **kwargs: _original_load(*args, **kwargs, weights_only=False)

from ultralytics import YOLO


MODEL_WEIGHTS = "yolov8m.pt"
DATA_YAML = "datasets/data_roi_crop.yaml"
RUN_NAME = "baseline_roi_crop_100epochs"
TRAIN_SAMPLE_SIZE = 1000
TRAIN_SAMPLE_SEED = 42
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def build_subset_data_yaml() -> Path:
    script_dir = Path(__file__).resolve().parent
    dataset_root = script_dir / "datasets" / "classroom_roi_crop"
    train_dir = dataset_root / "images" / "train"

    image_files = [
        path
        for path in sorted(train_dir.rglob("*"))
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    ]
    if len(image_files) < TRAIN_SAMPLE_SIZE:
        raise ValueError(
            f"Training set only has {len(image_files)} images, "
            f"but {TRAIN_SAMPLE_SIZE} were requested."
        )

    rng = random.Random(TRAIN_SAMPLE_SEED)
    sampled_images = rng.sample(image_files, TRAIN_SAMPLE_SIZE)

    temp_dir = Path(tempfile.mkdtemp(prefix="roi_crop_subset_"))
    train_list_path = temp_dir / "train_1000.txt"
    data_yaml_path = temp_dir / "data_roi_crop_1000.yaml"

    train_list_path.write_text(
        "\n".join(path.resolve().as_posix() for path in sampled_images) + "\n",
        encoding="gbk",
    )

    with open(script_dir / DATA_YAML, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    data["path"] = dataset_root.resolve().as_posix()
    data["train"] = train_list_path.resolve().as_posix()

    with open(data_yaml_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

    return data_yaml_path


if __name__ == "__main__":
    model = YOLO(MODEL_WEIGHTS)
    subset_data_yaml = build_subset_data_yaml()

    print("=" * 60)
    print("YOLOv8m baseline training on a random 1000-image ROI subset")
    print(f"Pretrained weights: {MODEL_WEIGHTS}")
    print(f"Data: {subset_data_yaml}")
    print(f"Run name: {RUN_NAME}")
    print("=" * 60)

    results = model.train(
        data=str(subset_data_yaml),
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
    print("ROI-cropped baseline training complete")
    print(f"Best model: runs/detect/{RUN_NAME}/weights/best.pt")
    print("=" * 60)
