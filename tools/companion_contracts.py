"""Authoritative Companion architecture contracts (ground truth for CI).

Human-readable mirror: docs/ARCHITECTURE_CONTRACTS.md
Derived from: CLAUDE.md, docs/ENTERPRISE_STACK.md, docs/HUMAN_INTERFACE.md,
docs/TESTING.md, and companion_interfaces/*.msg
"""
from __future__ import annotations

from dataclasses import dataclass

# --- Modularity (CLAUDE.md) ---
HARD_LINE_LIMIT = 800
SOFT_LINE_TARGET = 500
MAX_QOS_DEPTH = 10

# --- ROS distro (CLAUDE.md) ---
REQUIRED_ROS_DISTRO = 'jazzy'

# --- Shipped places.yaml (docs/HUMAN_INTERFACE.md) ---
# Kept in sync with companion_memory/places_contract.py (CI enforced).
REFERENCE_PLACES: dict[str, dict[str, float]] = {
    'kitchen': {'x': 3.2, 'y': 1.1, 'yaw': 1.57},
    'bedroom': {'x': -1.0, 'y': 4.5, 'yaw': 0.0},
    'dock': {'x': 0.0, 'y': 0.0, 'yaw': 0.0},
}

# --- Nav lifecycle (companion_body/nav_status.py) ---
NAV_STATUS_VALUES = frozenset({'idle', 'navigating', 'arrived', 'failed', 'following'})

# --- Agent lifecycle (companion_interfaces/AgentState.msg) ---
AGENT_STATE_VALUES = frozenset({
    'idle', 'listening', 'retrieving', 'thinking', 'speaking', 'acting', 'error',
})

# --- Behavior vocabulary (BehaviorRequest.msg + behavior_modes.py) ---
VALID_BEHAVIORS = frozenset({
    'idle', 'follow', 'patrol', 'go_to_place', 'play_with_dog', 'explore', 'stop', 'go_home',
})

BEHAVIOR_EMOTIONS = {
    'idle': 'neutral',
    'follow': 'happy',
    'patrol': 'neutral',
    'go_to_place': 'happy',
    'play_with_dog': 'happy',
    'explore': 'surprise',
    'stop': 'neutral',
    'go_home': 'love',
}

# --- MOAT empathy (companion_brain/human_to_robot.py) ---
EMPATHY_MIN_CONFIDENCE = 0.35
HUMAN_TO_ROBOT = {
    'happy': ('happy', 0.85),
    'sad': ('love', 0.9),
    'upset': ('sad', 0.75),
    'neutral': ('neutral', 0.6),
    'unknown': ('neutral', 0.5),
}

# --- Standard ROS topics allowed outside /companion/ namespace ---
ALLOWED_EXTERNAL_TOPICS = frozenset({
    '/goal_pose',  # Nav2 simple goal API
    '/image_raw',  # usb_cam desktop prototype
    '/ascamera/camera_publisher/rgb0/image',
    '/ascamera/camera_publisher/depth0/image_raw',
    '/ascamera/camera_publisher/rgb0/camera_info',
})

COMPANION_PACKAGES = frozenset({
    'companion_interfaces',
    'companion_brain',
    'companion_face',
    'companion_memory',
    'companion_agent',
    'companion_behaviors',
    'companion_body',
    'companion_perception',
    'companion_voice',
    'companion_bringup',
})


@dataclass(frozen=True)
class TopicContract:
    """One ROS topic contract: message type and allowed producer packages."""

    msg_type: str
    publishers: frozenset[str]
    subscribers: frozenset[str]


# Topic graph — must match docs/ARCHITECTURE_CONTRACTS.md
TOPIC_CONTRACTS: dict[str, TopicContract] = {
    '/companion/robot_emotion': TopicContract(
        msg_type='RobotEmotion',
        publishers=frozenset({
            'companion_brain', 'companion_behaviors',
        }),
        subscribers=frozenset({'companion_face', 'companion_voice'}),
    ),
    '/companion/human_emotion': TopicContract(
        msg_type='HumanEmotion',
        publishers=frozenset({'companion_perception'}),
        subscribers=frozenset({'companion_brain'}),
    ),
    '/companion/behavior_request': TopicContract(
        msg_type='BehaviorRequest',
        publishers=frozenset({'companion_agent'}),
        subscribers=frozenset({'companion_behaviors', 'companion_body'}),
    ),
    '/companion/voice_command': TopicContract(
        msg_type='String',
        publishers=frozenset({'companion_voice'}),
        subscribers=frozenset({'companion_agent'}),
    ),
    '/companion/agent_state': TopicContract(
        msg_type='AgentState',
        publishers=frozenset({'companion_agent', 'companion_voice'}),
        subscribers=frozenset({'companion_face'}),
    ),
    '/companion/tts_request': TopicContract(
        msg_type='String',
        publishers=frozenset({'companion_agent'}),
        subscribers=frozenset({'companion_voice'}),
    ),
    '/companion/tts_playing': TopicContract(
        msg_type='Bool',
        publishers=frozenset({'companion_voice'}),
        subscribers=frozenset({'companion_voice'}),
    ),
    '/companion/nav_status': TopicContract(
        msg_type='String',
        publishers=frozenset({'companion_body'}),
        subscribers=frozenset({'companion_agent'}),
    ),
    '/companion/detections': TopicContract(
        msg_type='DetectionBatch',
        publishers=frozenset({'companion_perception'}),
        subscribers=frozenset({'companion_body', 'companion_face'}),
    ),
    '/companion/detection_hint': TopicContract(
        msg_type='String',
        publishers=frozenset({'companion_perception'}),
        subscribers=frozenset({'companion_agent'}),
    ),
    '/companion/body_status': TopicContract(
        msg_type='String',
        publishers=frozenset({'companion_body'}),
        subscribers=frozenset(),
    ),
    '/companion/behavior_status': TopicContract(
        msg_type='String',
        publishers=frozenset({'companion_behaviors'}),
        subscribers=frozenset(),
    ),
    '/companion/camera_status': TopicContract(
        msg_type='String',
        publishers=frozenset({'companion_perception'}),
        subscribers=frozenset(),
    ),
    '/goal_pose': TopicContract(
        msg_type='PoseStamped',
        publishers=frozenset({'companion_body'}),
        subscribers=frozenset(),
    ),
}
