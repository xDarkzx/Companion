"""Named high-level behaviors the agent or voice layer can request."""
from dataclasses import dataclass

VALID_BEHAVIORS = frozenset({
    'idle',
    'follow',
    'patrol',
    'go_to_place',
    'harass_dog',
    'explore',
    'stop',
    'go_home',
})

BEHAVIOR_EMOTIONS = {
    'idle': 'neutral',
    'follow': 'happy',
    'patrol': 'neutral',
    'go_to_place': 'happy',
    'harass_dog': 'happy',
    'explore': 'surprise',
    'stop': 'neutral',
    'go_home': 'love',
}


@dataclass(frozen=True)
class BehaviorMode:
    """One active behavior with optional intensity."""

    name: str
    intensity: float = 0.8

    def __post_init__(self) -> None:
        if self.name not in VALID_BEHAVIORS:
            raise ValueError(f'Unknown behavior: {self.name}')
        if not 0.0 <= self.intensity <= 1.0:
            raise ValueError('intensity must be in [0, 1]')


def normalize_behavior(name: str) -> str:
    """Map aliases to canonical behavior names."""
    key = name.strip().lower().replace('-', '_').replace(' ', '_')
    aliases = {
        'follow_me': 'follow',
        'patrol_home': 'patrol',
        'patrol_the_home': 'patrol',
        'harass_dog': 'harass_dog',
        'harass_the_dog': 'harass_dog',
        'chase_dog': 'harass_dog',
        'go_explore': 'explore',
        'come_home': 'go_home',
        'home': 'go_home',
    }
    return aliases.get(key, key)
