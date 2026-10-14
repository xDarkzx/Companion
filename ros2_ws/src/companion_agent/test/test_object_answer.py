"""Unit tests for the spoken answer to a find request."""
import math

from companion_agent.object_answer import answer_for, bearing_phrase
import pytest


def point_at(degrees: float, distance: float = 1.2):
    rad = math.radians(degrees)
    return (distance * math.sin(rad), 0.0, distance * math.cos(rad))


@pytest.mark.parametrize('degrees, phrase', [
    (0.0, 'straight ahead'),
    (9.9, 'straight ahead'),
    (-9.9, 'straight ahead'),
    (10.1, 'ahead, a little to the right'),
    (-34.9, 'ahead, a little to the left'),
    (35.1, 'to your right'),
    (-60.0, 'to your left'),
])
def test_bearing_boundaries(degrees, phrase):
    assert bearing_phrase(point_at(degrees)) == phrase


def test_found_with_a_position_gives_distance_and_direction():
    text = answer_for('red mug', True, point_at(-20.0, 1.24))
    assert text == 'The red mug is about 1.2 metres ahead, a little to the left.'


def test_found_without_depth_says_so_instead_of_guessing():
    assert answer_for('red mug', True, None) == (
        "I can see the red mug, but I can't tell how far away it is."
    )


def test_not_found():
    assert answer_for('red mug', False, None) == "I can't see a red mug right now."


def test_one_metre_is_singular():
    assert 'about 1.0 metre ' in answer_for('mug', True, point_at(0.0, 1.0))


def test_unavailable_camera_is_said_plainly():
    from companion_agent.object_answer import answer_unavailable

    assert answer_unavailable() == "I can't check my camera right now."


def test_response_position_comes_from_the_best_placed_object():
    from companion_agent.object_answer import first_position
    from companion_interfaces.srv import FindObject
    from vision_msgs.msg import Detection3D

    response = FindObject.Response()
    assert first_position(response) is None
    det = Detection3D()
    det.bbox.center.position.x, det.bbox.center.position.z = 0.2, 1.5
    response.objects.detections.append(det)
    assert first_position(response) == (0.2, 0.0, 1.5)


def test_no_camera_frame_is_not_reported_as_object_missing():
    text = answer_for('mug', False, None, reason='no_frame')
    assert text == "I can't see anything yet: my camera hasn't sent a picture."
