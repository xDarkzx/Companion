"""Detect weak or gameable patterns in the Companion test suite."""
from __future__ import annotations

import re
from pathlib import Path

# Integration tests that publish to the graph must wait for subscribers first.
_PUBLISH_RE = re.compile(r'\.publish\s*\(')
_WAIT_RE = re.compile(r'wait_for_subscribers|require_subscribers|_wait_for_agent')
_LAUNCH_TEST_RE = re.compile(r'@pytest\.mark\.launch_test')
_PUBLISHER_RE = re.compile(r'create_publisher\s*\(')

# Patterns that indicate a test can pass without proving behavior.
_FORBIDDEN_PATTERNS = (
    (re.compile(r'\bassert\s+True\b'), 'assert True passes without checking behavior'),
    (re.compile(r'@pytest\.mark\.skip\b'), 'skipped test does not run'),
    (re.compile(r'@unittest\.skip\b'), 'skipped test does not run'),
    (re.compile(r'pytest\.skip\s*\('), 'skipped test does not run'),
)

# Loose coordinate checks when ground truth exists (places=1 allows ~10% error).
_LOOSE_COORD_RE = re.compile(
    r'assertAlmostEqual\s*\([^,]+,\s*[^,]+,\s*places\s*=\s*1\s*\)'
)

# Listener-only launch tests must warm up DDS before asserting.
_WARMUP_RE = re.compile(r'warm_up_dds|spin_until|spin_once')

_INTEGRATION_DIR_NAMES = ('test',)


def iter_integration_tests(ros_src: Path) -> list[Path]:
    """Return launch/integration test modules under companion packages."""
    files: list[Path] = []
    for pkg in sorted(ros_src.glob('companion_*')):
        test_dir = pkg / 'test'
        if not test_dir.is_dir():
            continue
        for path in sorted(test_dir.glob('test_*.py')):
            if path.name in {'test_flake8.py', 'test_pep257.py'}:
                continue
            files.append(path)
    return files


def validate_no_forbidden_patterns(test_files: list[Path]) -> list[str]:
    """Fail if tests contain skip/assert-True anti-patterns."""
    errors: list[str] = []
    for path in test_files:
        text = path.read_text(encoding='utf-8')
        for pattern, reason in _FORBIDDEN_PATTERNS:
            if pattern.search(text):
                errors.append(f'{path}: {reason}')
    return errors


def validate_launch_tests_wait_for_graph(test_files: list[Path]) -> list[str]:
    """Publishers in launch tests must wait for subscribers before publishing."""
    errors: list[str] = []
    for path in test_files:
        text = path.read_text(encoding='utf-8')
        if not _LAUNCH_TEST_RE.search(text):
            continue
        if not _PUBLISHER_RE.search(text):
            continue
        if not _PUBLISH_RE.search(text):
            continue
        if _WAIT_RE.search(text):
            continue
        errors.append(
            f'{path}: launch test publishes but never waits for subscribers '
            '(graph race — can pass while broken)',
        )
    return errors


def validate_listener_tests_warm_up(test_files: list[Path]) -> list[str]:
    """Launch tests without publishers must spin/warm up before assertions."""
    errors: list[str] = []
    for path in test_files:
        text = path.read_text(encoding='utf-8')
        if not _LAUNCH_TEST_RE.search(text):
            continue
        if _PUBLISHER_RE.search(text):
            continue
        if _WARMUP_RE.search(text):
            continue
        errors.append(
            f'{path}: listener-only launch test must warm_up_dds or spin before assert',
        )
    return errors


def validate_no_loose_coordinate_assertions(test_files: list[Path]) -> list[str]:
    """Ground-truth map coords must use tight tolerance (places=1 is too loose)."""
    errors: list[str] = []
    for path in test_files:
        text = path.read_text(encoding='utf-8')
        if _LOOSE_COORD_RE.search(text):
            errors.append(
                f'{path}: assertAlmostEqual(..., places=1) is too loose for map coords '
                '— use assert_pose_near or places>=2',
            )
    return errors


def validate_minimum_integration_coverage(ros_src: Path) -> list[str]:
    """Require behavioral integration tests for every critical pipeline stage."""
    required = {
        'test_companion_pipeline.py',
        'test_unknown_place_rejected.py',
        'test_stop_aborts_plan.py',
        'test_nav_stop_cancels.py',
        'test_empathy_flow.py',
        'test_behavior_emotion_contract.py',
        'test_follow_publishes_goal.py',
        'test_patrol_cycles_waypoints.py',
    }
    bringup_test = ros_src / 'companion_bringup' / 'test'
    present = {p.name for p in bringup_test.glob('test_*.py')}
    missing = sorted(required - present)
    if missing:
        return [f'missing required integration tests: {missing}']
    return []


def run_test_honesty_validators(ros_src: Path) -> list[str]:
    """Run all test-suite honesty checks."""
    tests = iter_integration_tests(ros_src)
    errors: list[str] = []
    for validator in (
        validate_no_forbidden_patterns,
        validate_launch_tests_wait_for_graph,
        validate_listener_tests_warm_up,
        validate_no_loose_coordinate_assertions,
    ):
        errors.extend(validator(tests))
    errors.extend(validate_minimum_integration_coverage(ros_src))
    return errors
