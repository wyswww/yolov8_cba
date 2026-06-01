# -*- coding: utf-8 -*-
"""ROI-cropped inference wrapper for YOLO models.

The wrapper crops an image before inference and maps predicted boxes back to
the original image coordinates. It is useful only for models trained on the
same ROI-cropped dataset.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


class ROIPredictor:
    """Callable wrapper that keeps the same basic interface as a YOLO model."""

    def __init__(
        self,
        model,
        left: float = 0.0,
        top: float = 0.06,
        right: float = 1.0,
        bottom: float = 1.0,
    ) -> None:
        if not (0.0 <= left < right <= 1.0):
            raise ValueError("ROI left/right must satisfy 0 <= left < right <= 1")
        if not (0.0 <= top < bottom <= 1.0):
            raise ValueError("ROI top/bottom must satisfy 0 <= top < bottom <= 1")
        self.model = model
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def __call__(self, source, *args, **kwargs):
        image, path = self._load_source(source)
        if image is None:
            return self.model(source, *args, **kwargs)

        h, w = image.shape[:2]
        x1, y1, x2, y2 = self._crop_box(w, h)
        cropped = image[y1:y2, x1:x2]
        results = self.model(cropped, *args, **kwargs)

        for result in results:
            self._map_result_to_original(result, image, path, x1, y1)
        return results

    def _crop_box(self, width: int, height: int) -> tuple[int, int, int, int]:
        x1 = max(0, int(round(self.left * width)))
        y1 = max(0, int(round(self.top * height)))
        x2 = min(width, int(round(self.right * width)))
        y2 = min(height, int(round(self.bottom * height)))
        return x1, y1, x2, y2

    @staticmethod
    def _load_source(source):
        if isinstance(source, np.ndarray):
            return source, None

        if isinstance(source, (str, Path)):
            path = str(source)
            data = np.fromfile(path, dtype=np.uint8)
            image = cv2.imdecode(data, cv2.IMREAD_COLOR)
            return image, path

        return None, None

    @staticmethod
    def _map_result_to_original(result, image: np.ndarray, path: str | None, offset_x: int, offset_y: int) -> None:
        result.orig_img = image
        result.orig_shape = image.shape[:2]
        if path is not None:
            result.path = path

        if result.boxes is None or len(result.boxes) == 0:
            return

        boxes = result.boxes.data.clone()
        boxes[:, [0, 2]] += offset_x
        boxes[:, [1, 3]] += offset_y
        result.update(boxes=boxes)
