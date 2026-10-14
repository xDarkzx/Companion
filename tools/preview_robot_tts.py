#!/usr/bin/env python3
"""Hear each robot TTS profile before batch-generating phrase clips."""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOICE_SRC = ROOT / 'ros2_ws' / 'src' / 'companion_voice'
if str(VOICE_SRC) not in sys.path:
    sys.path.insert(0, str(VOICE_SRC))

from companion_voice.robot_tts_profiles import (  # noqa: E402
    PREVIEW_LINES,
    ROBOT_TTS_PROFILES,
    get_profile,
)
from companion_voice.robot_tts_synth import synthesize_profile_wav  # noqa: E402
from companion_voice.wslg_audio import play_wav  # noqa: E402


def main() -> int:
    """Play sample lines for one or all profiles."""
    parser = argparse.ArgumentParser(description='Preview robot TTS profiles.')
    parser.add_argument('--profile', default='', help='Only this profile key')
    parser.add_argument(
        '--line',
        default=PREVIEW_LINES[0],
        help='Sample sentence to speak',
    )
    parser.add_argument(
        '--all-lines',
        action='store_true',
        help='Play three sample lines per profile',
    )
    args = parser.parse_args()

    profiles = ROBOT_TTS_PROFILES
    if args.profile.strip():
        profiles = (get_profile(args.profile),)

    lines = PREVIEW_LINES if args.all_lines else (args.line,)

    for profile in profiles:
        print(f'\n=== {profile.key}: {profile.label} ===')
        for line in lines:
            print(f'  "{line}"')
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as handle:
                path = Path(handle.name)
            try:
                synthesize_profile_wav(line, path, profile.key)
                play_wav(path, '')
            except RuntimeError as exc:
                print(f'  SKIP: {exc}')
            finally:
                path.unlink(missing_ok=True)

        try:
            input('  [Enter] next profile, Ctrl+C to quit ')
        except KeyboardInterrupt:
            print('\nStopped.')
            return 0

    print('\nPick a profile, then run:')
    print('  python3 tools/generate_robot_phrases.py --profile KEY --save-profile --play')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
