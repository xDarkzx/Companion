"""Map robot emotions to Piper synthesis parameters."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PiperEmotionProfile:
    """Lightweight expressivity knobs for Piper (Emo-style variation)."""

    length_scale: float = 1.0
    noise_scale: float = 0.667
    noise_w: float = 0.8


# Slightly faster/brighter for happy; slower/softer for sad — until EmojiVoice lands.
EMOTION_PROFILES: dict[str, PiperEmotionProfile] = {
    'neutral': PiperEmotionProfile(1.0, 0.667, 0.8),
    'happy': PiperEmotionProfile(0.92, 0.75, 0.85),
    'love': PiperEmotionProfile(0.95, 0.72, 0.82),
    'surprise': PiperEmotionProfile(0.88, 0.8, 0.9),
    'sad': PiperEmotionProfile(1.08, 0.55, 0.7),
    'cry': PiperEmotionProfile(1.12, 0.5, 0.65),
    'sleepy': PiperEmotionProfile(1.15, 0.5, 0.6),
    'focused': PiperEmotionProfile(0.98, 0.6, 0.75),
}


def profile_for_emotion(emotion: str) -> PiperEmotionProfile:
    """Return Piper knobs for the current robot mood."""
    return EMOTION_PROFILES.get(emotion.strip().lower(), EMOTION_PROFILES['neutral'])
