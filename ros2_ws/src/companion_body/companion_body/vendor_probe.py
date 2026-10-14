"""Detect whether MentorPi vendor packages are present in the workspace."""
from pathlib import Path

VENDOR_MARKERS = (
    'driver/package.xml',
    'peripherals/package.xml',
    'orchestrator_launch/package.xml',
)


def vendor_root() -> Path:
    """Return the vendor directory under ros2_ws/src/vendor."""
    src_dir = Path(__file__).resolve().parents[2]
    return src_dir / 'vendor'


def vendor_present() -> bool:
    """Return whether key MentorPi packages exist under ros2_ws/src/vendor."""
    root = vendor_root()
    return all((root / marker).is_file() for marker in VENDOR_MARKERS)
