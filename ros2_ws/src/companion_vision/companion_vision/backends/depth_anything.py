"""
Metric depth from one RGB image with Depth Anything V2 Metric Indoor Small.

The weights are the Transformers conversion of
depth-anything/Depth-Anything-V2-Metric-Hypersim-Small, published under Apache-2.0
(see docs/adr/0003).
"""
from __future__ import annotations

import numpy as np

MODEL_ID = 'depth-anything/Depth-Anything-V2-Metric-Indoor-Small-hf'
MODEL_REVISION = '8078d68a9c75a972131914f6afd0c1723be0da7f'


class MonocularDepth:
    """Estimate depth in metres for indoor scenes, resized back to the input resolution."""

    def __init__(self, *, device: str, revision: str | None = None) -> None:
        """Load the processor and model weights at a pinned revision."""
        import torch
        from transformers import AutoImageProcessor, AutoModelForDepthEstimation

        rev = revision or MODEL_REVISION
        self._torch = torch
        self._device = torch.device(device)
        self._processor = AutoImageProcessor.from_pretrained(MODEL_ID, revision=rev)
        model = AutoModelForDepthEstimation.from_pretrained(MODEL_ID, revision=rev)
        self._model = model.to(self._device).eval()

    def depth(self, rgb: np.ndarray, sensor: np.ndarray | None) -> np.ndarray | None:
        """Predict metric depth for the frame; any sensor frame is ignored."""
        height, width = rgb.shape[:2]
        inputs = self._processor(images=rgb, return_tensors='pt').to(self._device)
        with self._torch.inference_mode():
            outputs = self._model(**inputs)
        result = self._processor.post_process_depth_estimation(
            outputs, target_sizes=[(height, width)]
        )[0]
        return result['predicted_depth'].float().cpu().numpy()
