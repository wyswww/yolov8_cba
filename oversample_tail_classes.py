# -*- coding: utf-8 -*-
"""Create a train-only oversampled dataset for the two long-tail classes.

The script copies the original dataset and adds mild augmented copies only for
training images that contain:
  4: bowing the head
  5: leaning over the table

Validation and test splits are copied unchanged to keep evaluation fair.
"""

from __future__ import annotations

import random
import shutil
from collections import Counter
from pathlib import Path

import cv2
import numpy as np


RANDOM_SEED = 42
SOURCE_ROOT = Path("datasets") / "\u5b66\u751f\u8bfe\u5802\u884c\u4e3a\u68c0\u6d4b\u6570\u636e\u96c6"
OUTPUT_ROOT = Path("datasets") / "classroom_tail_oversampled"
DATA_YAML = Path("datasets") / "data_tail_oversampled.yaml"

CLASS_NAMES = [
    "hand-raising",
    "reading",
    "writing",
    "using phone",
    "bowing the head",
    "leaning over the table",
]
TAIL_CLASSES = {4, 5}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}

# Three focused crops lift tail classes without repeating every object in the
# original crowded classroom frame.
AUGMENTATIONS_PER_TAIL_IMAGE = 3


def cv_read_image(image_path: Path) -> np.ndarray | None:
    """Read images from paths that may contain non-ASCII characters on Windows."""
    data = np.fromfile(str(image_path), dtype=np.uint8)
    if data.size == 0:
        return None
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def cv_write_image(image_path: Path, image: np.ndarray) -> bool:
    """Write images to paths that may contain non-ASCII characters on Windows."""
    extension = image_path.suffix or ".jpg"
    ok, data = cv2.imencode(extension, image)
    if not ok:
        return False
    data.tofile(str(image_path))
    return True


def read_labels(label_path: Path) -> list[list[float]]:
    boxes: list[list[float]] = []
    if not label_path.exists():
        return boxes
    for line in label_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        parts = line.strip().split()
        if len(parts) < 5:
            continue
        cls = int(float(parts[0]))
        x, y, w, h = map(float, parts[1:5])
        boxes.append([cls, x, y, w, h])
    return boxes


def write_labels(label_path: Path, boxes: list[list[float]]) -> None:
    label_path.parent.mkdir(parents=True, exist_ok=True)
    with label_path.open("w", encoding="utf-8", newline="\n") as f:
        for cls, x, y, w, h in boxes:
            f.write(f"{int(cls)} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")


def list_images(split: str) -> list[Path]:
    image_dir = SOURCE_ROOT / "images" / split
    return sorted(p for p in image_dir.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS)


def image_to_label(image_path: Path, root: Path = SOURCE_ROOT) -> Path:
    split = image_path.parent.name
    return root / "labels" / split / f"{image_path.stem}.txt"


def copy_split(split: str) -> None:
    out_img_dir = OUTPUT_ROOT / "images" / split
    out_label_dir = OUTPUT_ROOT / "labels" / split
    out_img_dir.mkdir(parents=True, exist_ok=True)
    out_label_dir.mkdir(parents=True, exist_ok=True)

    for image_path in list_images(split):
        label_path = image_to_label(image_path)
        shutil.copy2(image_path, out_img_dir / image_path.name)
        if label_path.exists():
            shutil.copy2(label_path, out_label_dir / label_path.name)
        else:
            (out_label_dir / f"{image_path.stem}.txt").write_text("", encoding="utf-8")


def yolo_to_xyxy(box: list[float], img_w: int, img_h: int) -> np.ndarray:
    _, x, y, w, h = box
    return np.array(
        [
            [(x - w / 2) * img_w, (y - h / 2) * img_h],
            [(x + w / 2) * img_w, (y - h / 2) * img_h],
            [(x + w / 2) * img_w, (y + h / 2) * img_h],
            [(x - w / 2) * img_w, (y + h / 2) * img_h],
        ],
        dtype=np.float32,
    )


def box_xyxy_values(box: list[float], img_w: int, img_h: int) -> tuple[float, float, float, float]:
    corners = yolo_to_xyxy(box, img_w, img_h)
    x1, y1 = corners.min(axis=0)
    x2, y2 = corners.max(axis=0)
    return float(x1), float(y1), float(x2), float(y2)


def crop_around_tail(
    image: np.ndarray,
    boxes: list[list[float]],
) -> tuple[np.ndarray, list[list[float]]] | None:
    img_h, img_w = image.shape[:2]
    tail_boxes = [box for box in boxes if int(box[0]) in TAIL_CLASSES]
    if not tail_boxes:
        return None

    target = random.choice(tail_boxes)
    tx1, ty1, tx2, ty2 = box_xyxy_values(target, img_w, img_h)
    target_w = max(1.0, tx2 - tx1)
    target_h = max(1.0, ty2 - ty1)
    target_cx = (tx1 + tx2) / 2
    target_cy = (ty1 + ty2) / 2

    crop_w = max(target_w * random.uniform(3.5, 5.5), img_w * random.uniform(0.28, 0.45))
    crop_h = max(target_h * random.uniform(3.5, 5.5), img_h * random.uniform(0.28, 0.45))
    crop_w = min(crop_w, float(img_w))
    crop_h = min(crop_h, float(img_h))

    center_x = target_cx + random.uniform(-0.18, 0.18) * crop_w
    center_y = target_cy + random.uniform(-0.18, 0.18) * crop_h
    crop_x1 = int(round(np.clip(center_x - crop_w / 2, 0, img_w - crop_w)))
    crop_y1 = int(round(np.clip(center_y - crop_h / 2, 0, img_h - crop_h)))
    crop_x2 = int(round(crop_x1 + crop_w))
    crop_y2 = int(round(crop_y1 + crop_h))

    crop = image[crop_y1:crop_y2, crop_x1:crop_x2].copy()
    if crop.size == 0:
        return None

    out_h, out_w = crop.shape[:2]
    crop_boxes: list[list[float]] = []
    for box in boxes:
        cls = int(box[0])
        bx1, by1, bx2, by2 = box_xyxy_values(box, img_w, img_h)
        ix1 = max(bx1, crop_x1)
        iy1 = max(by1, crop_y1)
        ix2 = min(bx2, crop_x2)
        iy2 = min(by2, crop_y2)
        iw = ix2 - ix1
        ih = iy2 - iy1
        if iw < 3 or ih < 3:
            continue

        original_area = max(1.0, (bx2 - bx1) * (by2 - by1))
        visible_ratio = (iw * ih) / original_area
        min_visible = 0.25 if cls in TAIL_CLASSES else 0.55
        if visible_ratio < min_visible:
            continue

        nx1 = ix1 - crop_x1
        ny1 = iy1 - crop_y1
        nx2 = ix2 - crop_x1
        ny2 = iy2 - crop_y1
        crop_boxes.append(
            [
                cls,
                ((nx1 + nx2) / 2) / out_w,
                ((ny1 + ny2) / 2) / out_h,
                (nx2 - nx1) / out_w,
                (ny2 - ny1) / out_h,
            ]
        )

    if not any(int(box[0]) in TAIL_CLASSES for box in crop_boxes):
        return None
    return crop, crop_boxes


def transformed_boxes(
    boxes: list[list[float]],
    matrix: np.ndarray,
    img_w: int,
    img_h: int,
) -> list[list[float]]:
    result: list[list[float]] = []
    for box in boxes:
        cls = int(box[0])
        corners = yolo_to_xyxy(box, img_w, img_h)
        ones = np.ones((corners.shape[0], 1), dtype=np.float32)
        moved = np.hstack([corners, ones]) @ matrix.T

        x1, y1 = moved.min(axis=0)
        x2, y2 = moved.max(axis=0)
        x1 = float(np.clip(x1, 0, img_w - 1))
        y1 = float(np.clip(y1, 0, img_h - 1))
        x2 = float(np.clip(x2, 0, img_w - 1))
        y2 = float(np.clip(y2, 0, img_h - 1))

        bw = x2 - x1
        bh = y2 - y1
        if bw < 3 or bh < 3:
            continue

        original_area = box[3] * img_w * box[4] * img_h
        if original_area > 0 and (bw * bh) / original_area < 0.25:
            continue

        result.append(
            [
                cls,
                ((x1 + x2) / 2) / img_w,
                ((y1 + y2) / 2) / img_h,
                bw / img_w,
                bh / img_h,
            ]
        )
    return result


def mild_augment(image: np.ndarray, boxes: list[list[float]]) -> tuple[np.ndarray, list[list[float]]]:
    img_h, img_w = image.shape[:2]

    angle = random.uniform(-3.0, 3.0)
    scale = random.uniform(0.92, 1.08)
    tx = random.uniform(-0.04, 0.04) * img_w
    ty = random.uniform(-0.04, 0.04) * img_h

    matrix = cv2.getRotationMatrix2D((img_w / 2, img_h / 2), angle, scale)
    matrix[0, 2] += tx
    matrix[1, 2] += ty
    augmented = cv2.warpAffine(
        image,
        matrix,
        (img_w, img_h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT_101,
    )
    new_boxes = transformed_boxes(boxes, matrix, img_w, img_h)

    if random.random() < 0.5:
        augmented = cv2.flip(augmented, 1)
        for box in new_boxes:
            box[1] = 1.0 - box[1]

    alpha = random.uniform(0.88, 1.12)
    beta = random.uniform(-12.0, 12.0)
    augmented = cv2.convertScaleAbs(augmented, alpha=alpha, beta=beta)

    if random.random() < 0.25:
        augmented = cv2.GaussianBlur(augmented, (3, 3), 0)

    if random.random() < 0.25:
        noise = np.random.normal(0, 3, augmented.shape).astype(np.float32)
        augmented = np.clip(augmented.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    return augmented, new_boxes


def count_classes(label_root: Path) -> Counter[int]:
    counter: Counter[int] = Counter()
    for label_path in sorted(label_root.rglob("*.txt")):
        for box in read_labels(label_path):
            counter[int(box[0])] += 1
    return counter


def write_data_yaml() -> None:
    DATA_YAML.write_text(
        """# Train split with long-tail oversampling. Val/test are unchanged.
path: ..
train: datasets/\u5b66\u751f\u8bfe\u5802\u884c\u4e3a\u68c0\u6d4b\u6570\u636e\u96c6_tail_oversampled/images/train
train: datasets/classroom_tail_oversampled/images/train
val: datasets/classroom_tail_oversampled/images/val
test: datasets/classroom_tail_oversampled/images/test

nc: 6
names:
  - hand-raising
  - reading
  - writing
  - using phone
  - bowing the head
  - leaning over the table
""",
        encoding="utf-8",
    )


def main() -> None:
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    if not SOURCE_ROOT.exists():
        raise FileNotFoundError(f"Source dataset not found: {SOURCE_ROOT}")

    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)

    print(f"Source: {SOURCE_ROOT}")
    print(f"Output: {OUTPUT_ROOT}")

    for split in ("train", "val", "test"):
        copy_split(split)

    tail_images = []
    for image_path in list_images("train"):
        boxes = read_labels(image_to_label(image_path))
        if any(int(box[0]) in TAIL_CLASSES for box in boxes):
            tail_images.append((image_path, boxes))

    print(f"Tail-class train images: {len(tail_images)}")

    out_img_dir = OUTPUT_ROOT / "images" / "train"
    out_label_dir = OUTPUT_ROOT / "labels" / "train"
    generated = 0

    for image_path, boxes in tail_images:
        image = cv_read_image(image_path)
        if image is None:
            continue

        for aug_idx in range(AUGMENTATIONS_PER_TAIL_IMAGE):
            cropped = crop_around_tail(image, [box.copy() for box in boxes])
            if cropped is None:
                continue
            crop_image, crop_boxes = cropped
            aug_image, aug_boxes = mild_augment(crop_image, crop_boxes)
            if not any(int(box[0]) in TAIL_CLASSES for box in aug_boxes):
                continue

            stem = f"{image_path.stem}_tailos{aug_idx + 1}"
            out_image = out_img_dir / f"{stem}{image_path.suffix.lower()}"
            out_label = out_label_dir / f"{stem}.txt"
            if cv_write_image(out_image, aug_image):
                write_labels(out_label, aug_boxes)
                generated += 1

    write_data_yaml()

    train_counts = count_classes(OUTPUT_ROOT / "labels" / "train")
    print(f"Generated augmented train images: {generated}")
    print("Train label counts after oversampling:")
    for idx, name in enumerate(CLASS_NAMES):
        print(f"  {idx}: {name} = {train_counts[idx]}")
    print(f"Data config: {DATA_YAML}")


if __name__ == "__main__":
    main()
