# -*- coding: utf-8 -*-
"""继续训练 — 从 last.pt 接续"""

import torch
from ultralytics.nn.tasks import DetectionModel

# PyTorch 2.6 compatibility
torch.serialization.add_safe_globals([DetectionModel])
_original_load = torch.load
def _patched_load(*args, **kwargs):
    if "weights_only" not in kwargs:
        kwargs["weights_only"] = False
    return _original_load(*args, **kwargs)
torch.load = _patched_load

from ultralytics import YOLO

if __name__ == "__main__":
    model = YOLO("runs/detect/coordatt_backbone_eca_neck_v2/weights/last.pt")
    model.train(resume=True)
