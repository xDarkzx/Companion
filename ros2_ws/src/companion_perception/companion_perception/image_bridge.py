"""Convert sensor_msgs/Image to numpy arrays for CPU vision (no cv_bridge required)."""
from __future__ import annotations

from sensor_msgs.msg import Image

_SUPPORTED = frozenset({'rgb8', 'bgr8', 'mono8'})


def image_to_bgr(msg: Image):
    """Return an HxWx3 BGR uint8 array, or None if encoding is unsupported."""
    encoding = msg.encoding.strip().lower()
    if encoding not in _SUPPORTED:
        return None
    if msg.height < 1 or msg.width < 1:
        return None

    try:
        import numpy as np
    except ImportError:
        return None

    row_bytes = msg.step if msg.step > 0 else msg.width * (1 if encoding == 'mono8' else 3)
    needed = row_bytes * msg.height
    if len(msg.data) < needed:
        return None

    raw = np.frombuffer(bytes(msg.data[:needed]), dtype=np.uint8)
    if encoding == 'mono8':
        gray = raw.reshape(msg.height, row_bytes)[:, : msg.width]
        return np.stack([gray, gray, gray], axis=-1)

    frame = raw.reshape(msg.height, row_bytes)[:, : msg.width * 3]
    frame = frame.reshape(msg.height, msg.width, 3)
    if encoding == 'rgb8':
        return frame[:, :, ::-1].copy()
    return frame.copy()
