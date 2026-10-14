"""Prove the test suite cannot pass on lies — validators fail on bad input."""
from __future__ import annotations

import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
_ROOT = _TOOLS.parent
sys.path.insert(0, str(_TOOLS))
sys.path.insert(0, str(_ROOT / 'ros2_ws' / 'src' / 'companion_memory'))

from check_file_length import find_violations  # noqa: E402
from companion_contracts import TOPIC_CONTRACTS  # noqa: E402
from companion_memory.places_contract import REFERENCE_PLACES as MEMORY_PLACES  # noqa: E402
from validate_companion_architecture import (  # noqa: E402
    collect_topic_constants,
    iter_node_files,
    ros_src,
    scan_pub_sub,
    validate_behavior_msg_comment,
    validate_no_print_in_nodes,
    validate_topic_message_types,
)
from validate_test_honesty import run_test_honesty_validators  # noqa: E402


def test_honesty_validators_pass():
    """Integration tests must follow anti-fudge rules."""
    errors = run_test_honesty_validators(ros_src())
    assert errors == [], 'Test honesty violations:\n  ' + '\n  '.join(errors)


def test_places_contract_matches_tools_ground_truth():
    """Single source of truth: memory places_contract == tools companion_contracts."""
    from companion_contracts import REFERENCE_PLACES as TOOLS_PLACES  # noqa: WPS433

    assert MEMORY_PLACES == TOOLS_PLACES


def test_validators_catch_oversized_file(tmp_path: Path):
    """800-line guard must fail on deliberate overflow (not a rubber-stamp)."""
    (tmp_path / 'bloated.py').write_text('x\n' * 900, encoding='utf-8')
    assert find_violations(tmp_path, limit=800)


def test_validators_catch_print_in_fake_node(tmp_path: Path):
    """Architecture scan must reject print() in node modules."""
    pkg = tmp_path / 'companion_fake'
    mod = pkg / 'companion_fake'
    mod.mkdir(parents=True)
    (mod / 'fake_node.py').write_text(
        'def main():\n    print("nope")\n    destroy_node()\n    rclpy.shutdown()\n',
        encoding='utf-8',
    )
    errors = validate_no_print_in_nodes(tmp_path)
    assert any('print()' in e for e in errors)


def test_validators_catch_wrong_msg_type(tmp_path: Path):
    """Topic contract validator must reject String on DetectionBatch topic."""
    pkg = tmp_path / 'companion_perception'
    mod = pkg / 'companion_perception'
    mod.mkdir(parents=True)
    (mod / 'bad_node.py').write_text(
        'DETECTION_TOPIC = "/companion/detections"\n'
        'QUEUE_DEPTH = 10\n'
        'def x(self):\n'
        '    self.create_publisher(String, DETECTION_TOPIC, QUEUE_DEPTH)\n',
        encoding='utf-8',
    )
    errors = validate_topic_message_types(tmp_path)
    assert any('DetectionBatch' in e for e in errors)


def test_validators_catch_behavior_msg_drift(tmp_path: Path):
    """Behavior vocabulary drift in .msg must fail validation."""
    iface = tmp_path / 'companion_interfaces' / 'msg'
    iface.mkdir(parents=True)
    (iface / 'BehaviorRequest.msg').write_text(
        'string behavior    # idle, follow\n',
        encoding='utf-8',
    )
    errors = validate_behavior_msg_comment(tmp_path)
    assert errors


def test_topic_graph_is_wired_in_code():
    """Every contracted topic must appear on at least one pub or sub in nodes."""
    src = ros_src()
    pubs: set[str] = set()
    subs: set[str] = set()
    for path in iter_node_files(src):
        for _msg, topic in scan_pub_sub(path)[0]:
            pubs.add(topic)
        for _msg, topic in scan_pub_sub(path)[1]:
            subs.add(topic)

    errors: list[str] = []
    for topic, contract in TOPIC_CONTRACTS.items():
        if topic not in pubs and topic not in subs:
            errors.append(f'{topic} defined in contract but unused in any *_node.py')
        if contract.publishers and topic not in pubs:
            errors.append(f'{topic} has no publisher in codebase')
        if contract.subscribers and topic not in subs:
            errors.append(f'{topic} has no subscriber in codebase')
    assert errors == [], 'Unwired topic graph:\n  ' + '\n  '.join(errors)


def test_all_contract_topics_use_companion_namespace_or_allowlist():
    """No shadow topics — every node constant must be documented."""
    from companion_contracts import ALLOWED_EXTERNAL_TOPICS  # noqa: WPS433

    src = ros_src()
    errors: list[str] = []
    for path in iter_node_files(src):
        for _name, topic in collect_topic_constants(path).items():
            if topic in TOPIC_CONTRACTS or topic in ALLOWED_EXTERNAL_TOPICS:
                continue
            if topic.startswith('/companion/'):
                errors.append(f'{path}: undocumented companion topic {topic!r}')
    assert errors == [], '\n  '.join(errors)
