"""Draw result boxes onto a copy of the frame for visual debugging (Foxglove, RViz)."""
from __future__ import annotations

from collections.abc import Sequence

from companion_vision.types import Located
import numpy as np

BOX_COLOUR = (0, 255, 120)
LINE_PX = 3


def draw_boxes(rgb: np.ndarray, located: Sequence[Located]) -> np.ndarray:
    """Return a copy of the frame with each match outlined; the input is not modified."""
    out = rgb.copy()
    height, width = out.shape[:2]
    for item in located:
        box = item.box.clip(width, height)
        x0, y0 = int(box.x0), int(box.y0)
        x1, y1 = max(x0 + 1, int(box.x1)), max(y0 + 1, int(box.y1))
        out[y0:min(y0 + LINE_PX, y1), x0:x1] = BOX_COLOUR
        out[max(y1 - LINE_PX, y0):y1, x0:x1] = BOX_COLOUR
        out[y0:y1, x0:min(x0 + LINE_PX, x1)] = BOX_COLOUR
        out[y0:y1, max(x1 - LINE_PX, x0):x1] = BOX_COLOUR
    return out
