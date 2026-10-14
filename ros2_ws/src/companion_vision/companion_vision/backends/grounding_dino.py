"""Grounding DINO tiny open-vocabulary detector (Apache-2.0 weights) via transformers."""
from __future__ import annotations

from collections.abc import Sequence

from companion_vision.detector import finalize, normalize_queries
from companion_vision.types import Box, Detection2D
import numpy as np

MODEL_ID = 'IDEA-Research/grounding-dino-tiny'
MODEL_REVISION = 'a2bb814dd30d776dcf7e30523b00659f4f141c71'
MAX_PROMPT_TOKENS = 256
TEXT_THRESHOLD = 0.25


def prompt_for(queries: Sequence[str]) -> str:
    """Grounding DINO expects lowercase phrases separated by full stops."""
    return '. '.join(queries) + '.'


def match_query(phrase: str, queries: Sequence[str]) -> str | None:
    """Map a phrase the model grounded back to the query it came from."""
    phrase = ' '.join(phrase.lower().split())
    if phrase in queries:
        return phrase
    candidates = [q for q in queries if q in phrase or phrase in q]
    return max(candidates, key=len) if candidates and phrase else None


class GroundingDinoDetector:
    """Ground each query phrase in the image; long query lists are split to fit the prompt."""

    name = 'grounding_dino'

    def __init__(
        self, *, device: str, score_threshold: float, revision: str | None = None
    ) -> None:
        """Load the processor and model weights at a pinned revision."""
        import torch
        from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor

        rev = revision or MODEL_REVISION
        self._torch = torch
        self._device = torch.device(device)
        self._threshold = score_threshold
        self._processor = AutoProcessor.from_pretrained(MODEL_ID, revision=rev)
        model = AutoModelForZeroShotObjectDetection.from_pretrained(MODEL_ID, revision=rev)
        self._model = model.to(self._device).eval()

    def chunks(self, queries: Sequence[str]) -> list[list[str]]:
        """Split queries into groups whose prompt stays under the model's token limit."""
        groups: list[list[str]] = []
        current: list[str] = []
        for query in queries:
            trial = current + [query]
            if current and len(self._processor.tokenizer(prompt_for(trial))['input_ids']) > (
                    MAX_PROMPT_TOKENS):
                groups.append(current)
                trial = [query]
            current = trial
        if current:
            groups.append(current)
        return groups

    def detect(self, rgb: np.ndarray, queries: Sequence[str]) -> list[Detection2D]:
        """Run one forward pass per prompt chunk and merge the results."""
        labels = list(normalize_queries(queries))
        height, width = rgb.shape[:2]
        found: list[Detection2D] = []
        for group in self.chunks(labels):
            inputs = self._processor(images=rgb, text=prompt_for(group), return_tensors='pt')
            inputs = inputs.to(self._device)
            with self._torch.inference_mode():
                outputs = self._model(**inputs)
            result = self._processor.post_process_grounded_object_detection(
                outputs,
                inputs['input_ids'],
                threshold=self._threshold,
                text_threshold=TEXT_THRESHOLD,
                target_sizes=[(height, width)],
            )[0]
            phrases = result['text_labels'] if 'text_labels' in result else result['labels']
            for box, score, phrase in zip(result['boxes'], result['scores'], phrases):
                label = match_query(str(phrase), group)
                if label is None:
                    continue
                x0, y0, x1, y1 = (float(v) for v in box.tolist())
                clipped = Box(x0, y0, max(x0, x1), max(y0, y1)).clip(width, height)
                found.append(Detection2D(label, float(score), clipped))
        return finalize(found, self._threshold)
