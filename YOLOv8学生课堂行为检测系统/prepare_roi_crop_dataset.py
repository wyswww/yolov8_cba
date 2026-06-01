# -*- coding: utf-8 -*-
"""Create a ROI-cropped YOLO dataset with synchronized label conversion.

This script is intended for classroom scenes where a fixed part of each image
contains irrelevant background, such as ceiling, wall, or image borders. It
creates a new dataset instead of modifying the original one.
"""

from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
CLASS_NAMES = [
    "hand-raising",
    "reading",
    "writing",
    "using phone",
    "bowing the head",
    "leaning over the table",
]


@dataclass
class CropStats:
    images: int = 0
    labels_in: int = 0
    labels_out: int = 0
    clipped: int = 0
    dropped: int = 0
    missing_labels: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a ROI-cropped classroom YOLO dataset.")
    parser.add_argument("--source-root", default="datasets/学生课堂行为检测数据集", help="Original dataset root.")
    parser.add_argument("--output-root", default="datasets/classroom_roi_crop", help="Output dataset root.")
    parser.add_argument("--yaml-out", default="datasets/data_roi_crop.yaml", help="Output data yaml.")
    parser.add_argument("--left", type=float, default=0.0, help="Crop left ratio, 0-1.")
    parser.add_argument("--top", type=float, default=0.06, help="Crop top ratio, 0-1.")
    parser.add_argument("--right", type=float, default=1.0, help="Crop right ratio, 0-1.")
    parser.add_argument("--bottom", type=float, default=1.0, help="Crop bottom ratio, 0-1.")
    parser.add_argument("--min-visibility", type=float, default=0.35, help="Minimum retained box area ratio.")
    parser.add_argument("--min-size", type=float, default=2.0, help="Minimum clipped bbox width/height in pixels.")
    parser.add_argument("--quality", type=int, default=95, help="JPEG save quality.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output directory if it exists.")
    parser.add_argument("--dry-run", action="store_true", help="Only report statistics, do not write files.")
    return parser.parse_args()


def validate_crop(args: argparse.Namespace) -> None:
    if not (0.0 <= args.left < args.right <= 1.0):
        raise ValueError("--left and --right must satisfy 0 <= left < right <= 1")
    if not (0.0 <= args.top < args.bottom <= 1.0):
        raise ValueError("--top and --bottom must satisfy 0 <= top < bottom <= 1")
    if not (0.0 <= args.min_visibility <= 1.0):
        raise ValueError("--min-visibility must be in [0, 1]")


def read_yolo_labels(label_path: Path) -> list[tuple[int, float, float, float, float]]:
    labels = []
    if not label_path.exists():
        return labels
    for line in label_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        parts = line.strip().split()
        if len(parts) < 5:
            continue
        try:
            cls = int(float(parts[0]))
            x, y, w, h = map(float, parts[1:5])
        except ValueError:
            continue
        if w <= 0 or h <= 0:
            continue
        labels.append((cls, x, y, w, h))
    return labels


def transform_labels(
    labels: list[tuple[int, float, float, float, float]],
    image_w: int,
    image_h: int,
    crop_box: tuple[int, int, int, int],
    min_visibility: float,
    min_size: float,
) -> tuple[list[str], int, int]:
    left, top, right, bottom = crop_box
    crop_w = right - left
    crop_h = bottom - top
    out_lines: list[str] = []
    clipped_count = 0
    dropped_count = 0

    for cls, x, y, w, h in labels:
        x1 = (x - w / 2) * image_w
        y1 = (y - h / 2) * image_h
        x2 = (x + w / 2) * image_w
        y2 = (y + h / 2) * image_h
        original_area = max(0.0, x2 - x1) * max(0.0, y2 - y1)
        if original_area <= 0:
            dropped_count += 1
            continue

        nx1 = max(x1, left)
        ny1 = max(y1, top)
        nx2 = min(x2, right)
        ny2 = min(y2, bottom)
        new_w = nx2 - nx1
        new_h = ny2 - ny1
        visible_area = max(0.0, new_w) * max(0.0, new_h)

        if new_w < min_size or new_h < min_size or visible_area / original_area < min_visibility:
            dropped_count += 1
            continue
        if nx1 != x1 or ny1 != y1 or nx2 != x2 or ny2 != y2:
            clipped_count += 1

        cx = ((nx1 + nx2) / 2 - left) / crop_w
        cy = ((ny1 + ny2) / 2 - top) / crop_h
        bw = new_w / crop_w
        bh = new_h / crop_h
        out_lines.append(f"{cls} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}")

    return out_lines, clipped_count, dropped_count


def image_files(split_image_dir: Path) -> list[Path]:
    return sorted(p for p in split_image_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS)


def process_split(args: argparse.Namespace, split: str) -> CropStats:
    source_root = Path(args.source_root)
    output_root = Path(args.output_root)
    src_images = source_root / "images" / split
    src_labels = source_root / "labels" / split
    out_images = output_root / "images" / split
    out_labels = output_root / "labels" / split
    stats = CropStats()

    if not args.dry_run:
        out_images.mkdir(parents=True, exist_ok=True)
        out_labels.mkdir(parents=True, exist_ok=True)

    files = image_files(src_images)
    for index, image_path in enumerate(files, start=1):
        label_path = src_labels / f"{image_path.stem}.txt"
        if not label_path.exists():
            stats.missing_labels += 1

        labels = read_yolo_labels(label_path)
        stats.labels_in += len(labels)

        with Image.open(image_path) as image:
            image = ImageOps.exif_transpose(image)
            image_w, image_h = image.size
            crop_box = (
                int(round(args.left * image_w)),
                int(round(args.top * image_h)),
                int(round(args.right * image_w)),
                int(round(args.bottom * image_h)),
            )
            crop_box = (
                max(0, crop_box[0]),
                max(0, crop_box[1]),
                min(image_w, crop_box[2]),
                min(image_h, crop_box[3]),
            )
            out_lines, clipped, dropped = transform_labels(
                labels,
                image_w,
                image_h,
                crop_box,
                args.min_visibility,
                args.min_size,
            )

            stats.images += 1
            stats.labels_out += len(out_lines)
            stats.clipped += clipped
            stats.dropped += dropped

            if args.dry_run:
                continue

            cropped = image.crop(crop_box)
            dst_image = out_images / image_path.name
            save_kwargs = {}
            if dst_image.suffix.lower() in {".jpg", ".jpeg"}:
                save_kwargs = {"quality": args.quality}
            elif dst_image.suffix.lower() == ".png":
                save_kwargs = {"compress_level": 1}
            cropped.save(dst_image, **save_kwargs)
            (out_labels / f"{image_path.stem}.txt").write_text(
                "\n".join(out_lines) + ("\n" if out_lines else ""),
                encoding="utf-8",
            )
            if index % 500 == 0:
                print(f"  {split}: processed {index}/{len(files)} images")

    return stats


def write_yaml(args: argparse.Namespace) -> None:
    yaml_path = Path(args.yaml_out)
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    output_root = Path(args.output_root).resolve().as_posix()
    text = "\n".join([
        "# ROI-cropped dataset config for classroom behavior detection.",
        f"path: {output_root}",
        "train: images/train",
        "val: images/val",
        "test: images/test",
        "",
        "nc: 6",
        "names:",
        *[f"  - {name}" for name in CLASS_NAMES],
        "",
    ])
    yaml_path.write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    validate_crop(args)

    source_root = Path(args.source_root)
    if not source_root.exists():
        raise FileNotFoundError(f"Source dataset not found: {source_root}")

    output_root = Path(args.output_root)
    if output_root.exists() and args.overwrite and not args.dry_run:
        shutil.rmtree(output_root)
    elif output_root.exists() and not args.dry_run:
        raise FileExistsError(f"Output exists: {output_root}. Use --overwrite to replace it.")

    print("ROI crop ratios:")
    print(f"  left={args.left}, top={args.top}, right={args.right}, bottom={args.bottom}")
    print(f"  min_visibility={args.min_visibility}, min_size={args.min_size}px")
    print(f"  dry_run={args.dry_run}")

    total = CropStats()
    for split in ("train", "val", "test"):
        stats = process_split(args, split)
        total.images += stats.images
        total.labels_in += stats.labels_in
        total.labels_out += stats.labels_out
        total.clipped += stats.clipped
        total.dropped += stats.dropped
        total.missing_labels += stats.missing_labels
        print(
            f"{split}: images={stats.images}, labels_in={stats.labels_in}, "
            f"labels_out={stats.labels_out}, clipped={stats.clipped}, dropped={stats.dropped}, "
            f"missing_labels={stats.missing_labels}"
        )

    print(
        f"total: images={total.images}, labels_in={total.labels_in}, labels_out={total.labels_out}, "
        f"clipped={total.clipped}, dropped={total.dropped}, missing_labels={total.missing_labels}"
    )
    if total.labels_in:
        kept = total.labels_out / total.labels_in * 100
        print(f"label keep ratio: {kept:.2f}%")

    if not args.dry_run:
        write_yaml(args)
        print(f"dataset written to: {output_root.resolve()}")
        print(f"yaml written to: {Path(args.yaml_out).resolve()}")


if __name__ == "__main__":
    main()
