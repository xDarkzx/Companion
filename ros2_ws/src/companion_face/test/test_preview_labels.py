"""Unit tests for vision preview label formatting."""
from companion_face.preview_labels import format_detection_lines
from companion_interfaces.msg import Detection


def _det(label: str, confidence: float) -> Detection:
    msg = Detection()
    msg.label = label
    msg.confidence = confidence
    msg.source = 'test'
    return msg


def test_format_skips_idle_labels():
    """Idle states must not clutter the overlay."""
    lines = format_detection_lines([
        _det('idle', 1.0),
        _det('person', 0.91),
    ])
    assert lines == ['person (91%)']


def test_format_shows_camera_status_when_alone():
    """Camera-ready placeholder should appear when no objects are found."""
    lines = format_detection_lines([_det('camera_ready', 1.0)])
    assert lines == ['camera_ready']
