# 01 YOLOv8m基线模型

## 1. 对应文件

- 训练脚本：`train_baseline_100epochs.py`
- 主要输出目录：`runs/detect/baseline_mAP_100epochs`
- 初始权重：`yolov8m.pt`
- 模型类型：标准YOLOv8m检测模型

## 2. 训练配置

| 配置项 | 设置 |
|---|---|
| 模型权重 | `yolov8m.pt` |
| 训练轮数 | `epochs=100` |
| 早停 | `patience=30` |
| 输入尺寸 | `imgsz=640` |
| batch size | `batch=8` |
| 优化器 | `AdamW` |
| 初始学习率 | `lr0=0.0005` |
| 最终学习率比例 | `lrf=0.01` |
| 权重衰减 | `weight_decay=0.0005` |
| warmup | `warmup_epochs=5.0` |
| 损失权重 | `box=7.5, cls=0.5, dfl=1.5` |
| 随机种子 | `seed=42` |

## 3. 数据增强策略

基线模型使用较完整的YOLO训练增强策略：

```python
hsv_h=0.015
hsv_s=0.5
hsv_v=0.4
degrees=5.0
translate=0.1
scale=0.3
shear=2.0
perspective=0.0002
fliplr=0.5
mosaic=0.8
mixup=0.1
copy_paste=0.05
close_mosaic=10
```

这些增强用于提升模型对光照、尺度、位置和场景变化的适应能力。`close_mosaic=10` 表示训练最后10个epoch关闭mosaic，让模型后期更接近真实图像分布。

## 4. 原理说明

YOLOv8m是YOLOv8系列中的中等规模模型，在检测精度和推理速度之间较为平衡。它主要由Backbone、Neck和Detect Head组成：

- Backbone负责提取图像特征。
- Neck负责融合不同尺度特征。
- Detect Head负责输出类别、边界框和置信度。

本模型没有修改网络结构，直接使用官方YOLOv8m预训练权重进行迁移学习。预训练权重已经在大规模通用数据集上学习到边缘、纹理、形状和目标结构等通用特征，因此比从零训练更稳定。

## 5. 特点

优点：

- 结构稳定，训练风险低。
- 预训练权重完整加载，收敛速度快。
- 推理速度和检测精度比较均衡。
- 适合作为所有改进实验的基准。

不足：

- 对课堂中的小目标和细粒度姿态区分仍有提升空间。
- 对少数类行为的学习容易受类别不均衡影响。
- 输入尺寸为640，对远距离学生行为细节保留有限。

## 6. 实验定位

该模型是项目中的正式baseline。后续所有改进模型都需要和它比较，判断改动是否真正有效。

从实验结果看，baseline本身已经比较强，因此后续简单加注意力或检测头不一定能超过它。这也是后来转向训练策略优化的重要原因。
