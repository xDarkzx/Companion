"""Ensure places_contract matches shipped YAML (anti-drift)."""
from pathlib import Path

from companion_memory.places_contract import REFERENCE_PLACES
from companion_memory.places_store import load_places


def test_shipped_yaml_matches_places_contract():
    """Ground truth dict must equal parsed bringup config."""
    yaml_path = (
        Path(__file__).resolve().parents[2]
        / 'companion_bringup'
        / 'config'
        / 'places.yaml'
    )
    loaded = load_places(yaml_path)
    for name, coords in REFERENCE_PLACES.items():
        assert name in loaded
        assert loaded[name].x == coords['x']
        assert loaded[name].y == coords['y']
        assert loaded[name].yaw == coords['yaw']
