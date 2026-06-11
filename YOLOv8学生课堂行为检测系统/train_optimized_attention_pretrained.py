"""
ECA Backbone Attention — 基于 COCO 预训练权重微调
================================================
使用方法: python train_optimized_attention_pretrained.py

与原始 optimized_attention_light 的唯一区别：
  加载 yolov8m.pt COCO 预训练权重 → 匹配层继承预训练参数，ECA 层随机初始化
"""

from ultralytics import YOLO

# 1. 从 YAML 构建模型（ECA 层随机初始化）
model = YOLO("ultralytics/cfg/models/v8/yolov8m-optimized-attention.yaml")

# 2. 加载 COCO 预训练权重（仅匹配层）
model.load("yolov8m.pt")
print("[OK] 已加载 yolov8m.pt，ECA 层保持随机初始化")

# 3. 训练（与原始 optimized_attention_light 完全相同的超参数）
model.train(
    data="datasets/data.yaml",
    epochs=50,            # 50 epoch 已基本收敛（参考之前训练曲线）
    batch=8,
    imgsz=640,
    cache=True,
    device=0,
    workers=0,
    optimizer="AdamW",
    lr0=0.0005,
    lrf=0.01,
    momentum=0.937,
    weight_decay=0.0005,
    warmup_epochs=5.0,
    warmup_momentum=0.8,
    warmup_bias_lr=0.1,
    cos_lr=False,
    freeze=10,              # 冻结 backbone 前10层，注意力层更快收敛
    box=7.5,
    cls=0.5,
    dfl=1.5,
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
    auto_augment="randaugment",
    erasing=0.4,
    close_mosaic=5,         # 更早关闭 mosaic 加速训练
    seed=42,
    deterministic=True,
    amp=True,
    val=True,
    plots=True,
    project="runs/detect",
    name="optimized_attention_coco_pretrained",
)
