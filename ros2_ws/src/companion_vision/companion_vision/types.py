"""Plain value types shared by every stage of the perception pipeline."""
from __future__ import annotations

from dataclasses import dataclass
import math

Point3 = tuple[float, float, float]


@dataclass(frozen=True)
class Box:
    """Axis-aligned image box in pixels: (x0, y0) top-left, (x1, y1) bottom-right."""

    x0: float
    y0: float
    x1: float
    y1: float

    def __post_init__(self) -> None:
        """Reject inverted corners so every box downstream has a real extent."""
        if self.x1 < self.x0 or self.y1 < self.y0:
            raise ValueError(f'inverted box: {self}')

    @property
    def width(self) -> float:
        """Horizontal extent in pixels."""
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        """Vertical extent in pixels."""
        return self.y1 - self.y0

    @property
    def area(self) -> float:
        """Area in square pixels."""
        return self.width * self.height

    @property
    def center(self) -> tuple[float, float]:
        """Centre point (u, v) in pixels."""
        return ((self.x0 + self.x1) / 2.0, (self.y0 + self.y1) / 2.0)

    def iou(self, other: Box) -> float:
        """Intersection over union with another box (0.0 when they do not overlap)."""
        ix = max(0.0, min(self.x1, other.x1) - max(self.x0, other.x0))
        iy = max(0.0, min(self.y1, other.y1) - max(self.y0, other.y0))
        inter = ix * iy
        union = self.area + other.area - inter
        return inter / union if union > 0.0 else 0.0

    def clip(self, width: int, height: int) -> Box:
        """Return the part of the box that lies inside a width x height image."""
        x0 = min(max(self.x0, 0.0), float(width))
        y0 = min(max(self.y0, 0.0), float(height))
        x1 = min(max(self.x1, x0), float(width))
        y1 = min(max(self.y1, y0), float(height))
        return Box(x0, y0, x1, y1)


@dataclass(frozen=True)
class Detection2D:
    """One object a detector found for a text query."""

    label: str
    score: float
    box: Box


@dataclass(frozen=True)
class Intrinsics:
    """Pinhole camera intrinsics in pixels."""

    fx: float
    fy: float
    cx: float
    cy: float

    @classmethod
    def from_fov(cls, width: int, height: int, hfov_deg: float) -> Intrinsics:
        """Approximate intrinsics for an uncalibrated camera from its horizontal field of view."""
        focal = (width / 2.0) / math.tan(math.radians(hfov_deg) / 2.0)
        return cls(fx=focal, fy=focal, cx=width / 2.0, cy=height / 2.0)


@dataclass(frozen=True)
class Located:
    """A detection with its 3D position in the camera optical frame, when depth allowed one."""

    label: str
    score: float
    box: Box
    xyz: Point3 | None

    @classmethod
    def from_detection(cls, det: Detection2D, xyz: Point3 | None) -> Located:
        """Attach a 3D position (or None) to a 2D detection."""
        return cls(label=det.label, score=det.score, box=det.box, xyz=xyz)

    @property
    def distance(self) -> float | None:
        """Straight-line distance from the camera in metres, or None without a position."""
        if self.xyz is None:
            return None
        return math.sqrt(sum(c * c for c in self.xyz))
