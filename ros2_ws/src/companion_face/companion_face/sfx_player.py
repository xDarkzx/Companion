"""Play robot SFX from asset files (Emo-style clips) with synth fallback."""
from __future__ import annotations

from io import BytesIO
import math
from pathlib import Path
import struct
import wave

from companion_face.sfx_bank import EMOTION_TO_SFX, resolve_sfx_path
import pygame


def _tone(hz: float, ms: int, volume: float = 0.35) -> pygame.mixer.Sound:
    """Synthesize a short sine blip when no asset file exists."""
    rate = 22050
    n = int(rate * ms / 1000)
    buf = bytearray()
    for i in range(n):
        t = i / rate
        sample = int(volume * 32767 * math.sin(2 * math.pi * hz * t))
        buf += struct.pack('<h', sample)
    bio = BytesIO()
    with wave.open(bio, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(buf)
    bio.seek(0)
    return pygame.mixer.Sound(file=bio)


class SfxPlayer:
    """Play emotion-matched sounds from assets/sfx or fallback bleeps."""

    def __init__(self, enabled: bool = True, assets_dir: str = '') -> None:
        self._enabled = enabled
        self._ready = False
        self._assets = Path(assets_dir) if assets_dir else None
        self._files: dict[str, pygame.mixer.Sound] = {}
        self._fallback: dict[str, pygame.mixer.Sound] = {}
        if not enabled:
            return
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        self._load_assets()
        self._fallback = {
            'blink': _tone(880, 40, 0.25),
            'yawn': _tone(220, 180, 0.2),
            'happy': _tone(660, 60, 0.3),
            'sad': _tone(330, 120, 0.25),
            'listen': _tone(520, 50, 0.28),
            'think': _tone(400, 80, 0.22),
            'confirm': _tone(740, 45, 0.3),
            'alert': _tone(280, 140, 0.35),
        }
        self._ready = True

    def _load_assets(self) -> None:
        """Load WAV/OGG clips from the configured assets directory."""
        if self._assets is None or not self._assets.is_dir():
            return
        for key in (
            'blink', 'yawn', 'happy', 'love', 'surprise', 'sad', 'neutral',
            'listen', 'think', 'confirm', 'alert', 'wake',
        ):
            path = resolve_sfx_path(self._assets, key)
            if path is not None:
                self._files[key] = pygame.mixer.Sound(str(path))

    def _play_key(self, key: str) -> None:
        if not self._ready:
            return
        if key in self._files:
            self._files[key].play()
        elif key in self._fallback:
            self._fallback[key].play()

    def play_blink(self) -> None:
        """Play blink SFX."""
        self._play_key('blink')

    def play_yawn(self) -> None:
        """Play sleepy/yawn SFX."""
        self._play_key('yawn')

    def play_for_emotion(self, emotion: str) -> None:
        """Play a clip matched to the current face emotion."""
        key = EMOTION_TO_SFX.get(emotion.lower(), 'neutral')
        self._play_key(key)
