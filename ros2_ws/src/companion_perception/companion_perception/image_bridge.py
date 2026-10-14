"""Convert between sensor_msgs/Image and numpy arrays (no cv_bridge required)."""
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


def image_to_rgb(msg: Image):
    """Return an HxWx3 RGB uint8 array (what the vision models expect), or None."""
    bgr = image_to_bgr(msg)
    return None if bgr is None else bgr[:, :, ::-1].copy()


_DEPTH_DTYPES = {'16uc1': '<u2', 'mono16': '<u2', '32fc1': '<f4'}


def depth_image_to_array(msg: Image):
    """Return depth as HxW uint16 millimetres (16UC1) or float32 metres (32FC1), or None."""
    import numpy as np

    dtype = _DEPTH_DTYPES.get(msg.encoding.strip().lower())
    if dtype is None or msg.height < 1 or msg.width < 1:
        return None
    itemsize = np.dtype(dtype).itemsize
    row_bytes = msg.step if msg.step > 0 else msg.width * itemsize
    needed = row_bytes * msg.height
    if len(msg.data) < needed:
        return None
    rows = np.frombuffer(bytes(msg.data[:needed]), dtype=np.uint8).reshape(msg.height, row_bytes)
    pixels = rows[:, : msg.width * itemsize].copy().view(dtype)
    return pixels.reshape(msg.height, msg.width).astype(dtype[1:])


def rgb_to_image(rgb) -> Image:
    """Wrap an HxWx3 RGB uint8 array as an rgb8 sensor_msgs/Image."""
    msg = Image()
    msg.height, msg.width = int(rgb.shape[0]), int(rgb.shape[1])
    msg.encoding = 'rgb8'
    msg.step = msg.width * 3
    msg.data = rgb.astype('uint8', copy=False).tobytes()
    return msg
