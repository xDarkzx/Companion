"""Load named map places from YAML (kitchen, bedroom, dock)."""
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class PlacePose:
    """Map-frame goal for a named place."""

    name: str
    x: float
    y: float
    yaw: float


def load_places(path: Path) -> dict[str, PlacePose]:
    """Parse places.yaml into a name → pose lookup."""
    if not path.is_file():
        return {}

    raw = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    places_block = raw.get('places', {})
    result: dict[str, PlacePose] = {}
    for name, pose in places_block.items():
        if not isinstance(pose, dict):
            continue
        result[name.strip().lower()] = PlacePose(
            name=name.strip().lower(),
            x=float(pose['x']),
            y=float(pose['y']),
            yaw=float(pose.get('yaw', 0.0)),
        )
    return result


def list_place_names(path: Path) -> frozenset[str]:
    """Return known place names for command parsing."""
    return frozenset(load_places(path).keys())
