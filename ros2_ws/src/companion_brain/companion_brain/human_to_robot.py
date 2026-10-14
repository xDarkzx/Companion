"""Map perceived human affect to caring robot emotions."""
from __future__ import annotations

_HUMAN_TO_ROBOT = {
    'happy': ('happy', 0.85),
    'sad': ('love', 0.9),
    'upset': ('sad', 0.75),
    'neutral': ('neutral', 0.6),
    'unknown': ('neutral', 0.5),
}

MIN_CONFIDENCE = 0.35


def robot_response(human_emotion: str, confidence: float) -> tuple[str, float]:
    """Choose a RobotEmotion label and intensity from human affect."""
    if confidence < MIN_CONFIDENCE:
        return 'neutral', 0.5
    key = human_emotion.strip().lower()
    return _HUMAN_TO_ROBOT.get(key, ('neutral', 0.5))
