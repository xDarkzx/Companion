"""Static validators: Companion codebase vs architecture contracts."""
from __future__ import annotations

import ast
import re
from pathlib import Path

from companion_contracts import (
    ALLOWED_EXTERNAL_TOPICS,
    COMPANION_PACKAGES,
    HARD_LINE_LIMIT,
    MAX_QOS_DEPTH,
    SOFT_LINE_TARGET,
    TOPIC_CONTRACTS,
    VALID_BEHAVIORS,
)

_SKIP_DIRS = {'build', 'install', 'log', '__pycache__', 'vendor', 'test'}
_NODE_SUFFIX = '_node.py'
_LAUNCH_RE = re.compile(
    r"package\s*=\s*['\"](companion_[^'\"]+)['\"].*?"
    r"executable\s*=\s*['\"]([^'\"]+)['\"]",
    re.DOTALL,
)


def repo_root() -> Path:
    """Return repository root (parent of tools/)."""
    return Path(__file__).resolve().parent.parent


def ros_src() -> Path:
    """Return ros2_ws/src path."""
    return repo_root() / 'ros2_ws' / 'src'


def iter_companion_python(root: Path, *, include_tests: bool = False) -> list[Path]:
    """List Python files under companion_* packages."""
    files: list[Path] = []
    for pkg in sorted(root.glob('companion_*')):
        if not pkg.is_dir():
            continue
        for path in pkg.rglob('*.py'):
            if any(part in _SKIP_DIRS for part in path.parts):
                continue
            if not include_tests and 'test' in path.parts:
                continue
            files.append(path)
    return files


def iter_node_files(root: Path) -> list[Path]:
    """Return all ROS node entrypoint modules."""
    return [p for p in iter_companion_python(root) if p.name.endswith(_NODE_SUFFIX)]


def package_name_for(path: Path, src_root: Path) -> str:
    """Extract companion_* package name from a file path."""
    rel = path.relative_to(src_root)
    return rel.parts[0]


def parse_setup_executables(setup_path: Path) -> dict[str, str]:
    """Return executable -> 'package.module' from setup.py console_scripts."""
    text = setup_path.read_text(encoding='utf-8')
    collapsed = re.sub(r"'\s*\n\s*'", '', text)
    mapping: dict[str, str] = {}
    for match in re.finditer(
        r"'([a-z_]+)\s*=\s*([a-z_]+)\.([a-z_]+):main'",
        collapsed,
    ):
        exe, pkg, module = match.groups()
        mapping[exe] = f'{pkg}.{module}'
    return mapping


def parse_launch_executables(launch_dir: Path) -> list[tuple[str, str, str]]:
    """Return (launch_file, package, executable) tuples."""
    entries: list[tuple[str, str, str]] = []
    for launch in sorted(launch_dir.glob('*.launch.py')):
        text = launch.read_text(encoding='utf-8')
        for match in _LAUNCH_RE.finditer(text):
            pkg, exe = match.groups()
            entries.append((launch.name, pkg, exe))
    return entries


def collect_topic_constants(path: Path) -> dict[str, str]:
    """Map constant names to topic strings in a module."""
    text = path.read_text(encoding='utf-8')
    mapping: dict[str, str] = {}
    for match in re.finditer(
        r"^([A-Z][A-Z0-9_]*)\s*=\s*['\"](/[^'\"]+)['\"]",
        text,
        re.MULTILINE,
    ):
        mapping[match.group(1)] = match.group(2)
    if 'TOPIC' in mapping:
        pass
    single = re.search(r"^TOPIC\s*=\s*['\"](/[^'\"]+)['\"]", text, re.MULTILINE)
    if single:
        mapping['TOPIC'] = single.group(1)
    return mapping


def resolve_topic(arg: str, constants: dict[str, str]) -> str | None:
    """Resolve a create_publisher/subscription topic argument."""
    arg = arg.strip()
    if arg.startswith(("'", '"')):
        return arg.strip("'\"")
    return constants.get(arg)


def scan_pub_sub(path: Path) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Return (publishers, subscribers) as (msg_type, topic) pairs."""
    text = path.read_text(encoding='utf-8')
    constants = collect_topic_constants(path)
    pubs: list[tuple[str, str]] = []
    subs: list[tuple[str, str]] = []

    pub_re = re.compile(
        r'create_publisher\(\s*(\w+)\s*,\s*([^,\)]+)',
    )
    sub_re = re.compile(
        r'create_subscription\(\s*(\w+)\s*,\s*([^,\)]+)',
    )
    for msg_type, topic_arg in pub_re.findall(text):
        topic = resolve_topic(topic_arg, constants)
        if topic:
            pubs.append((msg_type, topic))
    for msg_type, topic_arg in sub_re.findall(text):
        topic = resolve_topic(topic_arg, constants)
        if topic:
            subs.append((msg_type, topic))
    return pubs, subs


def validate_package_names(src: Path) -> list[str]:
    """Ensure only companion_* packages exist under ros2_ws/src (excluding vendor)."""
    errors: list[str] = []
    for path in sorted(src.iterdir()):
        if not path.is_dir():
            continue
        name = path.name
        if name == 'vendor':
            continue
        if not name.startswith('companion_'):
            errors.append(f'non-companion package in src: {name}')
        elif name not in COMPANION_PACKAGES:
            errors.append(f'unknown companion package (update contracts): {name}')
    return errors


def validate_line_limits(src: Path) -> list[str]:
    """Enforce soft (500) and hard (800) line limits on production Python."""
    errors: list[str] = []
    for path in iter_companion_python(src, include_tests=False):
        count = sum(1 for _ in path.open(encoding='utf-8', errors='replace'))
        if count > HARD_LINE_LIMIT:
            errors.append(f'{path}: {count} lines exceeds hard cap {HARD_LINE_LIMIT}')
        elif count > SOFT_LINE_TARGET:
            errors.append(
                f'{path}: {count} lines exceeds soft target {SOFT_LINE_TARGET} — split file'
            )
    return errors


def validate_topic_namespaces(src: Path) -> list[str]:
    """All custom topics must use /companion/ or be in ALLOWED_EXTERNAL_TOPICS."""
    errors: list[str] = []
    for path in iter_node_files(src):
        for _name, topic in collect_topic_constants(path).items():
            if topic.startswith('/companion/'):
                continue
            if topic in ALLOWED_EXTERNAL_TOPICS:
                continue
            errors.append(f'{path}: topic {topic!r} not under /companion/ and not allowlisted')
    return errors


def validate_no_print_in_nodes(src: Path) -> list[str]:
    """ROS nodes must log via get_logger(), never print() (CLAUDE.md)."""
    errors: list[str] = []
    for path in iter_node_files(src):
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == 'print':
                    errors.append(f'{path}:{node.lineno}: print() forbidden in ROS nodes')
    return errors


def validate_shutdown_pattern(src: Path) -> list[str]:
    """Node main() must destroy_node and rclpy.shutdown in finally."""
    errors: list[str] = []
    for path in iter_node_files(src):
        text = path.read_text(encoding='utf-8')
        if 'def main' not in text:
            errors.append(f'{path}: missing main() entrypoint')
            continue
        if 'destroy_node' not in text:
            errors.append(f'{path}: main() must call destroy_node()')
        if 'rclpy.shutdown' not in text:
            errors.append(f'{path}: main() must call rclpy.shutdown() in finally')
    return errors


def validate_queue_depths(src: Path) -> list[str]:
    """QoS queue depth must be bounded (CLAUDE.md)."""
    errors: list[str] = []
    depth_re = re.compile(r'create_(?:publisher|subscription)\([^)]*,\s*(\d+)\s*\)')
    for path in iter_node_files(src):
        for match in depth_re.finditer(path.read_text(encoding='utf-8')):
            depth = int(match.group(1))
            if depth > MAX_QOS_DEPTH:
                errors.append(
                    f'{path}: QoS depth {depth} exceeds max {MAX_QOS_DEPTH}',
                )
    return errors


def validate_topic_message_types(src: Path) -> list[str]:
    """Publisher message types must match TOPIC_CONTRACTS."""
    errors: list[str] = []
    for path in iter_node_files(src):
        pkg = package_name_for(path, src)
        pubs, subs = scan_pub_sub(path)
        for msg_type, topic in pubs:
            contract = TOPIC_CONTRACTS.get(topic)
            if contract is None:
                if topic.startswith('/companion/'):
                    errors.append(f'{path}: publishes undocumented topic {topic!r}')
                continue
            if msg_type != contract.msg_type:
                errors.append(
                    f'{path}: {topic} must use {contract.msg_type}, not {msg_type}',
                )
            if pkg not in contract.publishers:
                errors.append(
                    f'{path}: package {pkg} may not publish {topic} '
                    f'(allowed: {sorted(contract.publishers)})',
                )
        for msg_type, topic in subs:
            contract = TOPIC_CONTRACTS.get(topic)
            if contract is None:
                continue
            if msg_type != contract.msg_type:
                errors.append(
                    f'{path}: subscribe {topic} must use {contract.msg_type}, not {msg_type}',
                )
            if contract.subscribers and pkg not in contract.subscribers:
                errors.append(
                    f'{path}: package {pkg} may not subscribe {topic} '
                    f'(allowed: {sorted(contract.subscribers)})',
                )
    return errors


def validate_launch_executables(src: Path) -> list[str]:
    """Every launch executable must exist in the owning package setup.py."""
    launch_dir = src / 'companion_bringup' / 'launch'
    if not launch_dir.is_dir():
        return [f'missing launch dir: {launch_dir}']

    setup_cache: dict[str, dict[str, str]] = {}
    errors: list[str] = []
    for _launch, pkg, exe in parse_launch_executables(launch_dir):
        setup = src / pkg / 'setup.py'
        if not setup.is_file():
            errors.append(f'launch references missing package {pkg}')
            continue
        if pkg not in setup_cache:
            setup_cache[pkg] = parse_setup_executables(setup)
        if exe not in setup_cache[pkg]:
            errors.append(
                f'{pkg}: launch executable {exe!r} not in setup.py console_scripts',
            )
    return errors


def validate_behavior_msg_comment(src: Path) -> list[str]:
    """BehaviorRequest.msg behavior list must match VALID_BEHAVIORS."""
    msg_path = src / 'companion_interfaces' / 'msg' / 'BehaviorRequest.msg'
    if not msg_path.is_file():
        return ['missing BehaviorRequest.msg']
    text = msg_path.read_text(encoding='utf-8')
    match = re.search(r'string behavior\s+#\s*([^\n]+)', text)
    if not match:
        return ['BehaviorRequest.msg missing behavior vocabulary comment']
    listed = {b.strip() for b in match.group(1).split(',') if b.strip()}
    if listed != VALID_BEHAVIORS:
        missing = VALID_BEHAVIORS - listed
        extra = listed - VALID_BEHAVIORS
        parts: list[str] = []
        if missing:
            parts.append(f'missing {sorted(missing)}')
        if extra:
            parts.append(f'extra {sorted(extra)}')
        return [f'BehaviorRequest.msg vocabulary mismatch: {"; ".join(parts)}']
    return []


def run_all_validators() -> list[str]:
    """Run every architecture validator and return combined error strings."""
    src = ros_src()
    errors: list[str] = []
    for validator in (
        validate_package_names,
        validate_line_limits,
        validate_topic_namespaces,
        validate_no_print_in_nodes,
        validate_shutdown_pattern,
        validate_queue_depths,
        validate_topic_message_types,
        validate_launch_executables,
        validate_behavior_msg_comment,
    ):
        errors.extend(validator(src))
    return errors
