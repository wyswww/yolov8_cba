# -*- coding: utf-8 -*-
# ====================== 🔥 修复 PyTorch 2.6 安全报错 ======================
import torch
from ultralytics.nn.tasks import DetectionModel
torch.serialization.add_safe_globals([DetectionModel])

_original_load = torch.load
torch.load = lambda *args, **kwargs: _original_load(*args, **kwargs, weights_only=False)
# ============================================================================


from ultralytics import YOLO

model_path = 'yolov8m.pt'
data_path = 'datasets/data.yaml'

if __name__ == '__main__':
    model = YOLO(model_path)
    results = model.train(data=data_path,
                          epochs=30,
                          batch=8,
                          device='0',
                          workers=0,
                          project='runs/detect',
                          name='exp_origin',
                          )








