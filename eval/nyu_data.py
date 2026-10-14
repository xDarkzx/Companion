"""Read the NYU Depth V2 labelled set and derive per-object ground truth in 3D.

The labelled file (nyu_depth_v2_labeled.mat, MATLAB v7.3) stores arrays column-major, so every
frame is transposed on read. Ground-truth positions use the in-filled `depths`; the depth-camera
path is evaluated on `rawDepths`, which keep the holes a real sensor has.
"""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from companion_vision.types import Box, Intrinsics
import numpy as np

# Standard Kinect RGB intrinsics for the NYU Depth V2 labelled set (640 x 480).
NYU_K = Intrinsics(fx=518.857901, fy=519.469611, cx=325.582449, cy=253.736166)
# Eigen et al. crop: the region with valid depth and no white border (top, left, bottom, right).
VALID_REGION = (45, 41, 471, 601)
MIN_INSTANCE_PIXELS = 500
CLASSES = ('chair', 'table', 'sofa', 'bed', 'pillow', 'lamp', 'monitor', 'television',
           'cabinet', 'door', 'bottle', 'cup', 'book', 'box')


@dataclass(frozen=True)
class Frame:
    """One labelled NYU frame."""

    index: int
    rgb: np.ndarray          # H x W x 3 uint8
    depth: np.ndarray        # H x W float32 metres, in-filled (ground truth)
    raw_depth: np.ndarray    # H x W float32 metres, raw sensor with zeros for holes
    labels: np.ndarray       # H x W class ids (0 = unlabelled)
    instances: np.ndarray    # H x W instance ids within a class


def split_test_indices(splits_path: Path) -> list[int]:
    """Zero-based indices of the official 654-image test split."""
    from scipy.io import loadmat

    return [int(i) - 1 for i in loadmat(str(splits_path))['testNdxs'].ravel()]


class NyuLabelled:
    """Random access to frames and class names in the labelled .mat file."""

    def __init__(self, path: Path) -> None:
        """Open the HDF5 file read-only."""
        import h5py

        self._file = h5py.File(str(path), 'r')
        refs = self._file['names'][0]
        self.names = [''.join(chr(c) for c in self._file[r][:].ravel()) for r in refs]

    def class_ids(self, wanted: tuple[str, ...] = CLASSES) -> dict[int, str]:
        """Map NYU class ids (1-based) to the chosen class names."""
        return {self.names.index(name) + 1: name for name in wanted}

    def frame(self, index: int) -> Frame:
        """Load one frame, transposed to row-major H x W layout."""
        f = self._file
        return Frame(
            index=index,
            rgb=np.ascontiguousarray(f['images'][index].transpose(2, 1, 0)),
            depth=np.ascontiguousarray(f['depths'][index].T),
            raw_depth=np.ascontiguousarray(f['rawDepths'][index].T),
            labels=np.ascontiguousarray(f['labels'][index].T),
            instances=np.ascontiguousarray(f['instances'][index].T),
        )

    def frames(self, indices: list[int]) -> Iterator[Frame]:
        """Yield frames in order."""
        for index in indices:
            yield self.frame(index)


def mask_box(mask: np.ndarray) -> Box:
    """Tight box around a mask, with the right and bottom edges exclusive."""
    rows = np.flatnonzero(mask.any(axis=1))
    cols = np.flatnonzero(mask.any(axis=0))
    return Box(float(cols[0]), float(rows[0]), float(cols[-1] + 1), float(rows[-1] + 1))


def gt_centroid(mask: np.ndarray, depth: np.ndarray, k: Intrinsics) -> tuple[float, float, float]:
    """Median 3D point of the object's visible surface (robust to stray mask pixels)."""
    rows, cols = np.nonzero(mask & (depth > 0))
    z = depth[rows, cols].astype(np.float64)
    x = (cols - k.cx) * z / k.fx
    y = (rows - k.cy) * z / k.fy
    return (float(np.median(x)), float(np.median(y)), float(np.median(z)))


def instances_in_frame(labels: np.ndarray, instances: np.ndarray,
                       class_ids: dict[int, str]) -> list[tuple[str, np.ndarray]]:
    """Objects of the chosen classes that are large enough and fully inside the valid region."""
    top, left, bottom, right = VALID_REGION
    found = []
    for class_id, name in class_ids.items():
        in_class = labels == class_id
        if not in_class.any():
            continue
        for instance_id in np.unique(instances[in_class]):
            mask = in_class & (instances == instance_id)
            if mask.sum() < MIN_INSTANCE_PIXELS:
                continue
            box = mask_box(mask)
            if box.y0 <= top or box.x0 <= left or box.y1 >= bottom or box.x1 >= right:
                continue
            found.append((name, mask))
    return found
