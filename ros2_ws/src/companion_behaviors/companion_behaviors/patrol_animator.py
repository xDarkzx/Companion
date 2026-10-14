"""Patrol face animation cycle (emotion names must match RobotEmotion.msg)."""
from dataclasses import dataclass

DEFAULT_PATROL_CYCLE = ('neutral', 'surprise', 'happy', 'neutral')


@dataclass(frozen=True)
class PatrolAnimation:
    """Timing for patrol mood cycling on the face."""

    emotions: tuple[str, ...]
    interval_sec: float

    @classmethod
    def from_params(cls, emotions: list[str], interval_sec: float) -> 'PatrolAnimation':
        """Build from ROS parameter lists."""
        names = tuple(emotions) if emotions else DEFAULT_PATROL_CYCLE
        return cls(emotions=names, interval_sec=max(0.5, float(interval_sec)))

    def emotion_at_tick(self, tick: int) -> str:
        """Return the patrol emotion for a given timer tick."""
        if not self.emotions:
            return 'neutral'
        return self.emotions[tick % len(self.emotions)]
