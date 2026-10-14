"""Unit tests for places.yaml loading."""
from pathlib import Path

from companion_memory.places_store import load_places


def test_load_places(tmp_path: Path):
    yaml_file = tmp_path / 'places.yaml'
    yaml_file.write_text(
        'places:\n  kitchen:\n    x: 1.0\n    y: 2.0\n    yaw: 0.5\n',
        encoding='utf-8',
    )
    places = load_places(yaml_file)
    assert 'kitchen' in places
    assert places['kitchen'].x == 1.0
    assert places['kitchen'].yaw == 0.5
