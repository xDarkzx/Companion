"""Convert companion_vision results to and from ROS messages (pure functions, no node)."""
from __future__ import annotations

from collections.abc import Sequence

from companion_interfaces.msg import Detection, DetectionBatch
from companion_interfaces.srv import FindObject
from companion_vision.types import Intrinsics, Located
from sensor_msgs.msg import CameraInfo
from std_msgs.msg import Header
from vision_msgs.msg import (
    Detection2D,
    Detection2DArray,
    Detection3D,
    Detection3DArray,
    ObjectHypothesisWithPose,
)


def intrinsics_from_camera_info(info: CameraInfo) -> Intrinsics | None:
    """Read fx, fy, cx, cy from the K matrix; None for an uncalibrated (all-zero) camera."""
    fx, fy = float(info.k[0]), float(info.k[4])
    if fx <= 0.0 or fy <= 0.0:
        return None
    return Intrinsics(fx=fx, fy=fy, cx=float(info.k[2]), cy=float(info.k[5]))


def _hypothesis(item: Located) -> ObjectHypothesisWithPose:
    result = ObjectHypothesisWithPose()
    result.hypothesis.class_id = item.label
    result.hypothesis.score = float(item.score)
    return result


def to_detection2d_array(located: Sequence[Located], header: Header) -> Detection2DArray:
    """Convert every match to an image-space box, best first."""
    array = Detection2DArray(header=header)
    for item in located:
        det = Detection2D(header=header)
        cx, cy = item.box.center
        det.bbox.center.position.x = cx
        det.bbox.center.position.y = cy
        det.bbox.size_x = item.box.width
        det.bbox.size_y = item.box.height
        det.results.append(_hypothesis(item))
        array.detections.append(det)
    return array


def to_detection3d_array(located: Sequence[Located], header: Header) -> Detection3DArray:
    """Convert matches that have a 3D position to points in the camera optical frame."""
    array = Detection3DArray(header=header)
    for item in located:
        if item.xyz is None:
            continue
        det = Detection3D(header=header)
        x, y, z = item.xyz
        det.bbox.center.position.x = x
        det.bbox.center.position.y = y
        det.bbox.center.position.z = z
        det.bbox.center.orientation.w = 1.0
        det.results.append(_hypothesis(item))
        array.detections.append(det)
    return array


def search_outcome(located: Sequence[Located]) -> tuple[bool, str]:
    """Decide (found, reason) for a FindObject response from the located matches."""
    reasons = FindObject.Response
    if not located:
        return False, reasons.REASON_NO_MATCH
    if any(item.xyz is not None for item in located):
        return True, reasons.REASON_OK
    return True, reasons.REASON_NO_DEPTH


def to_watch_batch(located: Sequence[Located], header: Header, source: str) -> DetectionBatch:
    """Build the watch-list batch for follow/hint consumers; 'none' when nothing is seen."""
    batch = DetectionBatch(header=header)
    for item in located or [None]:
        det = Detection()
        det.label = 'none' if item is None else item.label
        det.confidence = 1.0 if item is None else float(item.score)
        det.source = source
        batch.detections.append(det)
    return batch
