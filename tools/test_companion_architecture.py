"""Strict architecture contract tests — ground truth enforcement for Companion.

These tests prevent drift from tools/companion_contracts.py, ROS 2 Jazzy
guidelines (CLAUDE.md), and the message contracts in companion_interfaces.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(_TOOLS))

from check_file_length import find_violations  # noqa: E402
from companion_contracts import (  # noqa: E402
    BEHAVIOR_EMOTIONS,
    EMPATHY_MIN_CONFIDENCE,
    HUMAN_TO_ROBOT,
    NAV_STATUS_VALUES,
    REFERENCE_PLACES,
    VALID_BEHAVIORS,
)
from validate_companion_architecture import (  # noqa: E402
    ros_src,
    run_all_validators,
)


@pytest.fixture(scope='module')
def src_root() -> Path:
    """ROS 2 source tree."""
    return ros_src()


def test_architecture_validators_pass():
    """All static architecture validators must pass (zero drift)."""
    errors = run_all_validators()
    assert errors == [], 'Architecture violations:\n  ' + '\n  '.join(errors)


def test_hard_line_limit_800(src_root: Path):
    """CLAUDE.md hard cap: no production file may exceed 800 lines."""
    violations = find_violations(src_root, limit=800)
    prod = [v for v in violations if 'test' not in v[0].parts]
    assert prod == [], f'Files over 800 lines: {prod}'


def test_behavior_modes_match_contracts(src_root: Path):
    """behavior_modes.py must match authoritative VALID_BEHAVIORS + emotions."""
    sys.path.insert(0, str(src_root / 'companion_behaviors'))
    from companion_behaviors.behavior_modes import (  # noqa: WPS433
        BEHAVIOR_EMOTIONS as modes_emotions,
        VALID_BEHAVIORS as modes_behaviors,
    )

    assert modes_behaviors == VALID_BEHAVIORS
    assert modes_emotions == BEHAVIOR_EMOTIONS


def test_empathy_mapping_matches_contracts(src_root: Path):
    """human_to_robot.py must match MOAT contract (docs + empathy_node param)."""
    sys.path.insert(0, str(src_root / 'companion_brain'))
    from companion_brain.human_to_robot import (  # noqa: WPS433
        MIN_CONFIDENCE,
        _HUMAN_TO_ROBOT,
    )

    assert MIN_CONFIDENCE == EMPATHY_MIN_CONFIDENCE
    assert _HUMAN_TO_ROBOT == HUMAN_TO_ROBOT


def test_nav_status_module_matches_contracts(src_root: Path):
    """nav_status.py strings must match documented nav lifecycle."""
    sys.path.insert(0, str(src_root / 'companion_body'))
    from companion_body.nav_status import (  # noqa: WPS433
        ARRIVED,
        FAILED,
        FOLLOWING,
        IDLE,
        NAVIGATING,
    )

    assert {IDLE, NAVIGATING, ARRIVED, FAILED, FOLLOWING} == NAV_STATUS_VALUES


def test_shipped_places_yaml_matches_documentation(src_root: Path):
    """config/places.yaml must match the reference coordinates in the contracts."""
    sys.path.insert(0, str(src_root / 'companion_memory'))
    from companion_memory.places_store import load_places  # noqa: WPS433

    places_path = src_root / 'companion_bringup' / 'config' / 'places.yaml'
    loaded = load_places(places_path)
    for name, coords in REFERENCE_PLACES.items():
        assert name in loaded, f'missing documented place {name!r}'
        place = loaded[name]
        assert place.x == coords['x'], f'{name}.x drift'
        assert place.y == coords['y'], f'{name}.y drift'
        assert place.yaw == coords['yaw'], f'{name}.yaw drift'


def test_empathy_node_default_confidence_matches_contract(src_root: Path):
    """empathy_node default min_confidence must match human_to_robot gate."""
    text = (src_root / 'companion_brain' / 'companion_brain' / 'empathy_node.py').read_text(
        encoding='utf-8',
    )
    assert f"declare_parameter('min_confidence', {EMPATHY_MIN_CONFIDENCE})" in text


def test_every_companion_package_has_package_xml(src_root: Path):
    """Each companion_* package must ship package.xml (ament convention)."""
    missing = [
        p.name
        for p in sorted(src_root.glob('companion_*'))
        if p.is_dir() and not (p / 'package.xml').is_file()
    ]
    assert missing == []
