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


def test_rgb_frames_keep_rgb_order():
    from companion_perception.image_bridge import image_to_rgb

    msg = _rgb_image(1, 1)
    msg.data = bytes([255, 0, 0])
    assert image_to_rgb(msg)[0, 0].tolist() == [255, 0, 0]


def test_bgr_frames_are_converted_to_rgb():
    from companion_perception.image_bridge import image_to_rgb

    msg = _rgb_image(1, 1)
    msg.encoding = 'bgr8'
    msg.data = bytes([255, 0, 0])
    assert image_to_rgb(msg)[0, 0].tolist() == [0, 0, 255]


def test_16uc1_depth_is_read_as_millimetres():
    import numpy as np
    from companion_perception.image_bridge import depth_image_to_array

    msg = Image()
    msg.height, msg.width, msg.encoding, msg.step = 1, 2, '16UC1', 4
    msg.data = np.array([1500, 0], dtype='<u2').tobytes()
    depth = depth_image_to_array(msg)
    assert depth.dtype == np.uint16
    assert depth.tolist() == [[1500, 0]]


def test_32fc1_depth_is_read_as_metres():
    import numpy as np
    from companion_perception.image_bridge import depth_image_to_array

    msg = Image()
    msg.height, msg.width, msg.encoding, msg.step = 1, 1, '32FC1', 4
    msg.data = np.array([1.25], dtype='<f4').tobytes()
    assert depth_image_to_array(msg).tolist() == [[1.25]]


def test_unsupported_depth_encoding_is_none():
    from companion_perception.image_bridge import depth_image_to_array

    assert depth_image_to_array(_rgb_image(2, 2)) is None


def test_annotated_frames_round_trip_as_rgb8():
    import numpy as np
    from companion_perception.image_bridge import rgb_to_image

    rgb = np.zeros((2, 3, 3), dtype=np.uint8)
    rgb[0, 0] = (10, 20, 30)
    msg = rgb_to_image(rgb)
    assert (msg.encoding, msg.height, msg.width, msg.step) == ('rgb8', 2, 3, 9)
    assert bytes(msg.data[:3]) == bytes([10, 20, 30])
