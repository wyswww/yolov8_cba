# -*- coding: utf-8 -*-
"""
目标检测数据增强脚本
支持: Mosaic, MixUp, Copy-Paste, 随机旋转/缩放/平移/翻转
"""

import os
import random
import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm
import shutil

# 设置随机种子
random.seed(42)
np.random.seed(42)

# ==================== 配置 ====================
DATA_ROOT = Path("datasets/学生课堂行为检测数据集")
OUTPUT_ROOT = Path("datasets/学生课堂行为检测数据集_augmented")

# 增强参数
AUGMENTATION_COUNT = 3  # 每个原始样本生成3个增强样本

# Mosaic参数
MOSAIC_PROB = 0.5
MOSAIC_GRID = 2

# MixUp参数
MIXUP_PROB = 0.3
MIXUP_ALPHA = 0.5

# Copy-Paste参数
COPY_PASTE_PROB = 0.2
MIN_OBJECT_SIZE = 20  # 最小目标尺寸

# 基础变换参数
ROTATION_RANGE = 15
SCALE_RANGE = 0.3
TRANSLATE_RANGE = 0.1
FLIP_PROB = 0.5

# ==================== 配置 ====================


def load_yolo_label(label_path):
    """加载YOLO格式标签"""
    boxes = []
    if label_path.exists():
        with open(label_path, 'r') as f:
            for line in f.readlines():
                parts = line.strip().split()
                if len(parts) >= 5:
                    cls = int(parts[0])
                    x_center, y_center, w, h = map(float, parts[1:5])
                    boxes.append((cls, x_center, y_center, w, h))
    return boxes


def save_yolo_label(label_path, boxes):
    """保存YOLO格式标签"""
    label_path.parent.mkdir(parents=True, exist_ok=True)
    with open(label_path, 'w') as f:
        for box in boxes:
            cls, x, y, w, h = box
            f.write(f"{cls} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")


def box_xywh_to_xyxy(x, y, w, h, img_w, img_h):
    """YOLO格式转像素坐标"""
    x1 = int((x - w/2) * img_w)
    y1 = int((y - h/2) * img_h)
    x2 = int((x + w/2) * img_w)
    y2 = int((y + h/2) * img_h)
    return max(0, x1), max(0, y1), min(img_w-1, x2), min(img_h-1, y2)


def box_xyxy_to_yolo(x1, y1, x2, y2, img_w, img_h):
    """像素坐标转YOLO格式"""
    x = ((x1 + x2) / 2) / img_w
    y = ((y1 + y2) / 2) / img_h
    w = (x2 - x1) / img_w
    h = (y2 - y1) / img_h
    return x, y, w, h


def clip_box(x1, y1, x2, y2, img_w, img_h):
    """裁剪边界框到图像内"""
    x1 = max(0, min(x1, img_w - 1))
    y1 = max(0, min(y1, img_h - 1))
    x2 = max(0, min(x2, img_w - 1))
    y2 = max(0, min(y2, img_h - 1))
    return x1, y1, x2, y2


def apply_basic_augmentation(img, boxes, aug_idx):
    """应用基础变换增强"""
    h, w = img.shape[:2]

    # 随机旋转
    angle = random.uniform(-ROTATION_RANGE, ROTATION_RANGE)

    # 随机缩放
    scale = 1.0 + random.uniform(-SCALE_RANGE, SCALE_RANGE)

    # 随机翻转
    flip_horizontal = random.random() < FLIP_PROB

    # 随机亮度/对比度调整
    brightness = random.uniform(0.8, 1.2)
    contrast = random.uniform(0.8, 1.2)

    # 应用变换
    M = cv2.getRotationMatrix2D((w/2, h/2), angle, scale)

    if flip_horizontal:
        img = cv2.flip(img, 1)
        # 翻转边界框
        for i in range(len(boxes)):
            boxes[i] = (boxes[i][0], 1.0 - boxes[i][1], boxes[i][2], boxes[i][3], boxes[i][4])

    # 旋转边界框
    new_boxes = []
    for box in boxes:
        cls, x_c, y_c, w, h = box
        x1 = (x_c - w/2) * w
        y1 = (y_c - h/2) * h
        x2 = (x_c + w/2) * w
        y2 = (y_c + h/2) * h

        # 转换到像素坐标
        px1, py1 = x_c * w - w/2, y_c * h - h/2
        px2, py2 = x_c * w + w/2, y_c * h + h/2

        # 应用旋转变换
        points = np.array([[px1 * w, py1 * h],
                           [px2 * w, py2 * h],
                           [px1 * w, py2 * h],
                           [px2 * w, py1 * h]])

        if flip_horizontal:
            points[:, 0] = w - points[:, 0]

        # 计算新的边界框
        x_new = points[:, 0].mean() / w
        y_new = points[:, 1].mean() / h
        w_new = (points[:, 0].max() - points[:, 0].min()) / w
        h_new = (points[:, 1].max() - points[:, 1].min()) / h

        # 确保在有效范围内
        if 0 < x_new < 1 and 0 < y_new < 1 and 0 < w_new < 1 and 0 < h_new < 1:
            new_boxes.append((cls, x_new, y_new, w_new, h_new))

    # 应用颜色变换
    img = cv2.convertScaleAbs(img, alpha=contrast, beta=0)
    img = np.clip(img * brightness, 0, 255).astype(np.uint8)

    return img, new_boxes


def apply_mosaic(img1, boxes1, img2, boxes2, img3, boxes3, img4, boxes4):
    """应用Mosaic增强"""
    h, w = img1.shape[:2]

    # 创建输出图像
    mosaic_img = np.zeros((h * 2, w * 2, 3), dtype=np.uint8)

    # 随机选择布局
    layout = random.randint(0, 3)
    positions = [
        ((0, 0), (h, w)),
        ((0, w), (h, 2*w)),
        ((h, 0), (2*h, w)),
        ((h, w), (2*h, 2*w))
    ]

    imgs = [img1, img2, img3, img4]
    all_boxes = []

    for i, (pos, size) in enumerate(positions):
        y1, x1 = pos
        y2, x2 = size

        # 随机选择图像
        if i == layout:
            src_img = imgs[0]
            src_boxes = boxes1
        else:
            src_idx = random.randint(1, 3)
            src_img = imgs[src_idx]
            src_boxes = [boxes1, boxes2, boxes3, boxes4][src_idx]

        # 调整图像大小并放置
        src_resized = cv2.resize(src_img, (w, h))
        mosaic_img[y1:y2, x1:x2] = src_resized

        # 调整边界框坐标
        for box in src_boxes:
            cls, x_c, y_c, bw, bh = box

            # 缩放到新图像坐标系
            new_x = (x_c * w + x1) / (2 * w)
            new_y = (y_c * h + y1) / (2 * h)
            new_w = bw / 2
            new_h = bh / 2

            if 0 < new_x < 1 and 0 < new_y < 1 and new_w > 0 and new_h > 0:
                all_boxes.append((cls, new_x, new_y, new_w, new_h))

    # 调整到目标大小
    mosaic_img = cv2.resize(mosaic_img, (w, h))

    # 调整边界框
    final_boxes = []
    for box in all_boxes:
        cls, x_c, y_c, w, h = box
        if 0 < x_c < 1 and 0 < y_c < 1:
            final_boxes.append(box)

    return mosaic_img, final_boxes


def apply_mixup(img1, boxes1, img2, boxes2, alpha=0.5):
    """应用MixUp增强"""
    # 调整大小一致
    h, w = img1.shape[:2]
    img2_resized = cv2.resize(img2, (w, h))

    # 混合图像
    mixed_img = cv2.addWeighted(img1, alpha, img2_resized, 1 - alpha, 0)

    # 合并边界框
    all_boxes = boxes1 + boxes2

    # 过滤超出边界框
    final_boxes = []
    for box in all_boxes:
        cls, x_c, y_c, w, h = box
        if 0 < x_c < 1 and 0 < y_c < 1 and 0 < w < 1 and 0 < h < 1:
            final_boxes.append(box)

    return mixed_img, final_boxes


def apply_copy_paste(img, boxes, all_imgs, all_boxes, aug_idx):
    """应用Copy-Paste增强"""
    if len(all_imgs) < 2:
        return img, boxes

    h, w = img.shape[:2]
    new_boxes = boxes.copy()

    # 随机选择要复制的目标数量
    n_paste = random.randint(1, 5)

    for _ in range(n_paste):
        # 随机选择源图像
        src_idx = random.randint(0, len(all_imgs) - 1)
        src_img = all_imgs[src_idx]
        src_boxes = all_boxes[src_idx]

        if not src_boxes:
            continue

        # 随机选择要复制的目标
        box = random.choice(src_boxes)
        cls, x_c, y_c, bw, bh = box

        # 转换到像素坐标
        x1, y1, x2, y2 = box_xywh_to_xyxy(x_c, y_c, bw, bh, src_img.shape[1], src_img.shape[0])

        # 提取目标区域
        obj = src_img[y1:y2, x1:x2]
        if obj.size == 0:
            continue

        # 随机变换目标
        obj_h, obj_w = obj.shape[:2]

        # 随机缩放
        scale = random.uniform(0.5, 1.5)
        obj = cv2.resize(obj, (int(obj_w * scale), int(obj_h * scale)))
        obj_h, obj_w = obj.shape[:2]

        # 随机翻转
        if random.random() < 0.5:
            obj = cv2.flip(obj, 1)

        # 随机位置粘贴
        paste_x = random.randint(0, max(0, w - obj_w))
        paste_y = random.randint(0, max(0, h - obj_h))

        # 确保目标尺寸足够大
        if obj_w < MIN_OBJECT_SIZE or obj_h < MIN_OBJECT_SIZE:
            continue

        # 创建掩码
        mask = np.ones(obj.shape[:2], dtype=np.uint8) * 255
        if obj.shape[2] == 3:
            # 简单的前景检测（基于颜色）
            gray = cv2.cvtColor(obj, cv2.COLOR_BGR2GRAY)
            mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)[1]

        # 粘贴目标
        try:
            roi = img[paste_y:paste_y+obj_h, paste_x:paste_x+obj_w]
            for c in range(3):
                roi[:, :, c] = np.where(mask == 255, obj[:, :, c], roi[:, :, c])
            img[paste_y:paste_y+obj_h, paste_x:paste_x+obj_w] = roi

            # 添加新的边界框
            new_x = (paste_x + obj_w/2) / w
            new_y = (paste_y + obj_h/2) / h
            new_w = obj_w / w
            new_h = obj_h / h

            if 0 < new_x < 1 and 0 < new_y < 1 and 0 < new_w < 1 and 0 < new_h < 1:
                new_boxes.append((cls, new_x, new_y, new_w, new_h))
        except:
            continue

    return img, new_boxes


def augment_single_image(img_path, label_path, all_imgs, all_boxes, aug_idx, split):
    """对单张图片进行增强"""
    img = cv2.imread(str(img_path))
    if img is None:
        return None

    boxes = load_yolo_label(label_path)
    h, w = img.shape[:2]

    results = []

    # 1. 基础增强（多次）
    for i in range(AUGMENTATION_COUNT):
        aug_img, aug_boxes = apply_basic_augmentation(img.copy(), boxes.copy(), aug_idx + i)
        if len(aug_boxes) > 0:
            results.append((aug_img, aug_boxes))

    # 2. MixUp增强
    if random.random() < MIXUP_PROB and len(all_imgs) > 0:
        src_idx = random.randint(0, len(all_imgs) - 1)
        mix_img, mix_boxes = apply_mixup(img, boxes, all_imgs[src_idx], all_boxes[src_idx])
        if len(mix_boxes) > 0:
            results.append((mix_img, mix_boxes))

    # 3. Copy-Paste增强
    if random.random() < COPY_PASTE_PROB and len(all_imgs) > 1:
        cp_img, cp_boxes = apply_copy_paste(img.copy(), boxes.copy(), all_imgs, all_boxes, aug_idx)
        if len(cp_boxes) > 0:
            results.append((cp_img, cp_boxes))

    return results


def main():
    print("=" * 60)
    print("🎯 目标检测数据增强工具")
    print("=" * 60)

    for split in ['train', 'val', 'test']:
        print(f"\n📂 处理 {split} 集...")

        img_dir = DATA_ROOT / "images" / split
        label_dir = DATA_ROOT / "labels" / split
        output_img_dir = OUTPUT_ROOT / "images" / split
        output_label_dir = OUTPUT_ROOT / "labels" / split

        if not img_dir.exists():
            print(f"  ⚠️  {img_dir} 不存在，跳过")
            continue

        # 创建输出目录
        output_img_dir.mkdir(parents=True, exist_ok=True)
        output_label_dir.mkdir(parents=True, exist_ok=True)

        # 加载所有图片和标签
        img_files = list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.png"))
        all_imgs = []
        all_boxes = []

        print(f"  加载 {len(img_files)} 张图片...")
        for img_file in tqdm(img_files, desc=f"  加载"):
            img = cv2.imread(str(img_file))
            label_file = label_dir / f"{img_file.stem}.txt"
            boxes = load_yolo_label(label_file)
            all_imgs.append(img)
            all_boxes.append(boxes)

        # 生成增强数据
        print(f"  生成增强数据...")
        aug_count = 0

        for idx, img_file in enumerate(tqdm(img_files, desc=f"  增强")):
            label_file = label_dir / f"{img_file.stem}.txt"
            results = augment_single_image(img_file, label_file, all_imgs, all_boxes, idx, split)

            for aug_idx, (aug_img, aug_boxes) in enumerate(results):
                # 保存增强图片
                aug_img_name = f"{img_file.stem}_aug{aug_idx}.jpg"
                aug_label_name = f"{img_file.stem}_aug{aug_idx}.txt"

                aug_img_path = output_img_dir / aug_img_name
                aug_label_path = output_label_dir / aug_label_name

                cv2.imwrite(str(aug_img_path), aug_img)
                save_yolo_label(aug_label_path, aug_boxes)
                aug_count += 1

        # 复制原始数据
        print(f"  复制原始数据...")
        for img_file in tqdm(img_files, desc="  复制"):
            label_file = label_dir / f"{img_file.stem}.txt"
            if label_file.exists():
                shutil.copy(img_file, output_img_dir / img_file.name)
                shutil.copy(label_file, output_label_dir / label_file.name)

        print(f"  ✅ 完成: 原始 {len(img_files)} 张 → 增强后 {len(img_files) + aug_count} 张")

    print("\n" + "=" * 60)
    print("📁 增强后的数据集保存在:")
    print(f"   {OUTPUT_ROOT}")
    print("=" * 60)

    # 更新data.yaml
    yaml_content = f"""# 增强后的数据集配置
path: ../..
train: datasets/学生课堂行为检测数据集_augmented/images/train
val: datasets/学生课堂行为检测数据集_augmented/images/val
test: datasets/学生课堂行为检测数据集_augmented/images/test

nc: 6
names: ['hand-raising', 'reading', 'writing', 'using phone', 'bowing the head', 'leaning over the table']
"""

    with open("datasets/data_augmented.yaml", 'w') as f:
        f.write(yaml_content)

    print("\n✅ 数据集配置文件: datasets/data_augmented.yaml")
    print("\n开始训练增强后的数据:")
    print("python -c \"from ultralytics import YOLO; YOLO('yolov8m.pt').train(data='datasets/data_augmented.yaml', epochs=100)\"")


if __name__ == "__main__":
    main()