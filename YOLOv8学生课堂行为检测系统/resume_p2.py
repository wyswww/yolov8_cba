# -*- coding: utf-8 -*-
"""继续训练 yolov8m_p2_coco_pretrained — 从 last.pt 接续"""

import torch
from ultralytics.nn.tasks import DetectionModel

# PyTorch 2.6 compatibility
torch.serialization.add_safe_globals([DetectionModel])
_original_load = torch.load
torch.load = lambda *args, **kwargs: _original_load(*args, **kwargs, weights_only=False)

from ultralytics import YOLO

if __name__ == "__main__":
    model = YOLO("runs/detect/yolov8m_p2_coco_pretrained/weights/last.pt")
    model.train(resume=True)
