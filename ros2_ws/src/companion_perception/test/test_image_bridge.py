"""Unit tests for sensor_msgs/Image → numpy conversion."""
from companion_perception.image_bridge import image_to_bgr
from sensor_msgs.msg import Image


def _rgb_image(width: int, height: int, fill: int = 0) -> Image:
    msg = Image()
    msg.height = height
    msg.width = width
    msg.encoding = 'rgb8'
    msg.step = width * 3
    msg.data = bytes([fill] * (width * height * 3))
    return msg


def test_rgb8_to_bgr_shape():
    arr = image_to_bgr(_rgb_image(4, 2, fill=7))
    assert arr is not None
    assert arr.shape == (2, 4, 3)


def test_rgb8_channel_order():
    msg = Image()
    msg.height = 1
    msg.width = 1
    msg.encoding = 'rgb8'
    msg.step = 3
    msg.data = bytes([255, 0, 0])
    arr = image_to_bgr(msg)
    assert arr is not None
    assert arr[0, 0, 2] == 255  # red in RGB → BGR blue channel last


def test_unsupported_encoding_returns_none():
    msg = _rgb_image(2, 2)
    msg.encoding = '16UC1'
    assert image_to_bgr(msg) is None
