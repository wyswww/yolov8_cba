# -*- coding: utf-8 -*-
# ====================== 🔥 修复 PyTorch 2.6 安全报错 ======================
import torch
from ultralytics.nn.tasks import DetectionModel
torch.serialization.add_safe_globals([DetectionModel])

_original_load = torch.load
torch.load = lambda *args, **kwargs: _original_load(*args, **kwargs, weights_only=False)
# ============================================================================


from ultralytics import YOLO

model_path = 'yolov8m.pt'  # 原始预训练模型
data_path = 'datasets/data.yaml'

if __name__ == '__main__':
    model = YOLO(model_path)

    # 基线训练 - 使用合适的参数
    results = model.train(
        data=data_path,
        epochs=100,           # 增加到100个epoch
        patience=30,           # 早停耐心值
        batch=8,
        imgsz=640,            # 图片大小
        device='0',
        workers=0,
        project='runs/detect',
        name='baseline_mAP',  # 基线实验名称

        # 优化器设置
        optimizer='AdamW',    # 使用AdamW优化器
        lr0=0.001,            # 初始学习率
        lrf=0.01,             # 最终学习率
        weight_decay=0.0005,  # 权重衰减

        # 数据增强（关键！）
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10.0,          # 旋转
        translate=0.1,        # 平移
        scale=0.5,            # 缩放
        shear=0.0,
        perspective=0.0,
        flipud=0.0,
        fliplr=0.5,           # 左右翻转
        mosaic=1.0,           # 马赛克增强
        mixup=0.1,            # MixUp增强
        copy_paste=0.0,

        # 其他设置
        pretrained=True,      # 使用预训练权重
        verbose=True,        # 详细输出
        seed=0,              # 固定随机种子
        exist_ok=False,      # 不覆盖已有实验
    )








