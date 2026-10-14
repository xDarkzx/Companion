"""Unit tests for converting located objects to and from ROS messages."""
from companion_interfaces.srv import FindObject
from companion_perception.ros_convert import (
    intrinsics_from_camera_info,
    search_outcome,
    to_detection2d_array,
    to_detection3d_array,
    to_watch_batch,
)
from companion_vision.types import Box, Located
import pytest
from sensor_msgs.msg import CameraInfo
from std_msgs.msg import Header

HEADER = Header(frame_id='camera_color_optical_frame')
MUG = Located('mug', 0.8, Box(10.0, 20.0, 30.0, 60.0), (0.1, -0.2, 1.5))
MUG_NO_DEPTH = Located('mug', 0.6, Box(10.0, 20.0, 30.0, 60.0), None)


def test_camera_info_gives_intrinsics():
    info = CameraInfo()
    info.k = [500.0, 0.0, 320.0, 0.0, 510.0, 240.0, 0.0, 0.0, 1.0]
    k = intrinsics_from_camera_info(info)
    assert (k.fx, k.fy, k.cx, k.cy) == (500.0, 510.0, 320.0, 240.0)


def test_uncalibrated_camera_info_gives_none():
    assert intrinsics_from_camera_info(CameraInfo()) is None


def test_2d_detections_keep_label_score_and_box():
    array = to_detection2d_array([MUG], HEADER)
    [det] = array.detections
    assert array.header.frame_id == 'camera_color_optical_frame'
    assert det.results[0].hypothesis.class_id == 'mug'
    assert det.results[0].hypothesis.score == pytest.approx(0.8)
    assert (det.bbox.center.position.x, det.bbox.center.position.y) == (20.0, 40.0)
    assert (det.bbox.size_x, det.bbox.size_y) == (20.0, 40.0)


def test_3d_objects_carry_the_position_and_skip_unplaced_ones():
    array = to_detection3d_array([MUG, MUG_NO_DEPTH], HEADER)
    [obj] = array.detections
    position = obj.bbox.center.position
    assert (position.x, position.y, position.z) == pytest.approx((0.1, -0.2, 1.5))
    assert obj.results[0].hypothesis.class_id == 'mug'


def test_search_outcomes():
    assert search_outcome([MUG]) == (True, FindObject.Response.REASON_OK)
    assert search_outcome([MUG_NO_DEPTH]) == (True, FindObject.Response.REASON_NO_DEPTH)
    assert search_outcome([]) == (False, FindObject.Response.REASON_NO_MATCH)


def test_watch_batch_reports_none_when_nothing_is_seen():
    assert [d.label for d in to_watch_batch([], HEADER, 'owlv2').detections] == ['none']
    batch = to_watch_batch([MUG], HEADER, 'owlv2')
    assert [(d.label, d.source) for d in batch.detections] == [('mug', 'owlv2')]
