"""OWLv2 open-vocabulary detector (Apache-2.0 weights) via Hugging Face transformers."""
from __future__ import annotations

from collections.abc import Sequence

from companion_vision.detector import finalize, normalize_queries
from companion_vision.types import Box, Detection2D
import numpy as np

MODEL_ID = 'google/owlv2-base-patch16-ensemble'
MODEL_REVISION = 'cfd3195ba4ea9592eec887ded089f4c08eff231d'


class OwlV2Detector:
    """Score every query against every image region; keep confident, de-duplicated boxes."""

    name = 'owlv2'

    def __init__(
        self, *, device: str, score_threshold: float, revision: str | None = None
    ) -> None:
        """Load the processor and model weights at a pinned revision."""
        import torch
        from transformers import Owlv2ForObjectDetection, Owlv2Processor

        rev = revision or MODEL_REVISION
        self._torch = torch
        self._device = torch.device(device)
        self._threshold = score_threshold
        self._processor = Owlv2Processor.from_pretrained(MODEL_ID, revision=rev)
        model = Owlv2ForObjectDetection.from_pretrained(MODEL_ID, revision=rev)
        self._model = model.to(self._device).eval()

    def detect(self, rgb: np.ndarray, queries: Sequence[str]) -> list[Detection2D]:
        """Run one forward pass for all queries and map boxes back to image pixels."""
        labels = list(normalize_queries(queries))
        height, width = rgb.shape[:2]
        inputs = self._processor(text=[labels], images=rgb, return_tensors='pt').to(self._device)
        with self._torch.inference_mode():
            outputs = self._model(**inputs)
        # OWLv2 pads the image to a square at the bottom/right, so boxes scale by the long side.
        side = max(height, width)
        result = self._processor.post_process_grounded_object_detection(
            outputs=outputs,
            threshold=self._threshold,
            target_sizes=[(side, side)],
            text_labels=[labels],
        )[0]
        found = []
        for box, score, index in zip(result['boxes'], result['scores'], result['labels']):
            x0, y0, x1, y1 = (float(v) for v in box.tolist())
            clipped = Box(x0, y0, max(x0, x1), max(y0, y1)).clip(width, height)
            found.append(Detection2D(labels[int(index)], float(score), clipped))
        return finalize(found, self._threshold)
