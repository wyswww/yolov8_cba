# -*- coding: utf-8 -*-
"""
数据集重新划分脚本
按比例: train 70% / val 20% / test 10%
"""

import os
import shutil
import random
from pathlib import Path

# ==================== 配置 ====================
DATASET_ROOT = Path(__file__).parent / "datasets" / "学生课堂行为检测数据集"

# 划分比例
TRAIN_RATIO = 0.70
VAL_RATIO = 0.20
TEST_RATIO = 0.10

# 随机种子（保证可重复）
RANDOM_SEED = 42
# ==================== 配置 ====================

def get_all_samples(split_type):
    """获取指定划分下的所有图片"""
    img_dir = DATASET_ROOT / "images" / split_type
    if not img_dir.exists():
        return []
    return [f.stem for f in img_dir.glob("*.jpg")]

def move_files(sample_names, src_split, dst_split):
    """移动文件从源划分到目标划分"""
    images_dir = DATASET_ROOT / "images"
    labels_dir = DATASET_ROOT / "labels"

    moved = 0
    for stem in sample_names:
        # 移动图片
        src_img = images_dir / src_split / f"{stem}.jpg"
        dst_img = images_dir / dst_split / f"{stem}.jpg"
        if src_img.exists():
            shutil.move(str(src_img), str(dst_img))
            moved += 1

        # 移动标签
        src_label = labels_dir / src_split / f"{stem}.txt"
        dst_label = labels_dir / dst_split / f"{stem}.txt"
        if src_label.exists():
            shutil.move(str(src_label), str(dst_label))

    return moved

def main():
    random.seed(RANDOM_SEED)

    print("=" * 50)
    print("数据集重新划分脚本")
    print("=" * 50)
    print(f"\n数据集根目录: {DATASET_ROOT}")
    print(f"划分比例: train={TRAIN_RATIO*100:.0f}% / val={VAL_RATIO*100:.0f}% / test={TEST_RATIO*100:.0f}%")

    # 统计当前数据
    print("\n【当前数据分布】")
    train_samples = get_all_samples("train")
    val_samples = get_all_samples("val")
    test_samples = get_all_samples("test")
    total = len(train_samples) + len(val_samples) + len(test_samples)

    print(f"  train: {len(train_samples):3d} 张 (当前: {len(train_samples)/total*100:.1f}%)")
    print(f"  val:   {len(val_samples):3d} 张 (当前: {len(val_samples)/total*100:.1f}%)")
    print(f"  test:  {len(test_samples):3d} 张 (当前: {len(test_samples)/total*100:.1f}%)")
    print(f"  总计:  {total} 张")

    # 合并所有样本
    all_samples = train_samples + val_samples + test_samples
    random.shuffle(all_samples)

    # 计算划分数量
    n_train = int(len(all_samples) * TRAIN_RATIO)
    n_val = int(len(all_samples) * VAL_RATIO)
    n_test = len(all_samples) - n_train - n_val

    new_train = set(all_samples[:n_train])
    new_val = set(all_samples[n_train:n_train + n_val])
    new_test = set(all_samples[n_train + n_val:])

    print(f"\n【重新划分方案】")
    print(f"  train: {len(new_train):3d} 张 (目标: {TRAIN_RATIO*100:.0f}%)")
    print(f"  val:   {len(new_val):3d} 张 (目标: {VAL_RATIO*100:.0f}%)")
    print(f"  test:  {len(new_test):3d} 张 (目标: {TEST_RATIO*100:.0f}%)")

    # 确认目录存在
    for split in ["train", "val", "test"]:
        img_dir = DATASET_ROOT / "images" / split
        label_dir = DATASET_ROOT / "labels" / split
        img_dir.mkdir(parents=True, exist_ok=True)
        label_dir.mkdir(parents=True, exist_ok=True)

    # 移动文件
    print("\n【开始移动文件】")

    # 从 train 移动到 test/val（如果需要）
    train_to_move = [s for s in train_samples if s not in new_train]
    if train_to_move:
        # 优先移动到val，再移动到test
        to_val = [s for s in train_to_move if s in new_val]
        to_test = [s for s in train_to_move if s in new_test]
        n1 = move_files(to_val, "train", "val")
        n2 = move_files(to_test, "train", "test")
        print(f"  从 train 移动到 val:   {n1} 张")
        print(f"  从 train 移动到 test:  {n2} 张")

    # 从 val 移动到 train/test
    val_to_move = [s for s in val_samples if s not in new_val]
    if val_to_move:
        to_train = [s for s in val_to_move if s in new_train]
        to_test = [s for s in val_to_move if s in new_test]
        n1 = move_files(to_train, "val", "train")
        n2 = move_files(to_test, "val", "test")
        print(f"  从 val   移动到 train: {n1} 张")
        print(f"  从 val   移动到 test:  {n2} 张")

    # 从 test 移动到 train/val
    test_to_move = [s for s in test_samples if s not in new_test]
    if test_to_move:
        to_train = [s for s in test_to_move if s in new_train]
        to_val = [s for s in test_to_move if s in new_val]
        n1 = move_files(to_train, "test", "train")
        n2 = move_files(to_val, "test", "val")
        print(f"  从 test  移动到 train: {n1} 张")
        print(f"  从 test  移动到 val:   {n2} 张")

    # 验证最终结果
    print("\n【重新划分后的分布】")
    final_train = get_all_samples("train")
    final_val = get_all_samples("val")
    final_test = get_all_samples("test")
    final_total = len(final_train) + len(final_val) + len(final_test)

    print(f"  train: {len(final_train):3d} 张 ({len(final_train)/final_total*100:.1f}%)")
    print(f"  val:   {len(final_val):3d} 张 ({len(final_val)/final_total*100:.1f}%)")
    print(f"  test:  {len(final_test):3d} 张 ({len(final_test)/final_total*100:.1f}%)")
    print(f"  总计:  {final_total} 张")

    print("\n✅ 数据集重新划分完成！")
    print("\n现在可以运行训练:")
    print("  python train.py")


if __name__ == "__main__":
    main()
