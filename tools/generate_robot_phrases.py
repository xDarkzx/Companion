#!/usr/bin/env python3
"""Generate English robot phrase WAVs with a chosen TTS profile."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOICE_SRC = ROOT / 'ros2_ws' / 'src' / 'companion_voice'
if str(VOICE_SRC) not in sys.path:
    sys.path.insert(0, str(VOICE_SRC))

from companion_voice.reply_catalog import catalog_phrase_dict, extra_place_phrases  # noqa: E402
from companion_voice.robot_tts_profiles import (  # noqa: E402
    ROBOT_TTS_PROFILES,
    default_profile_key,
    get_profile,
)
from companion_voice.robot_tts_synth import synthesize_profile_wav  # noqa: E402


def _all_phrase_texts() -> dict[str, str]:
    """Catalog phrases plus any going_<place> lines from places.yaml."""
    phrases = dict(catalog_phrase_dict())
    places_file = ROOT / 'ros2_ws' / 'src' / 'companion_bringup' / 'config' / 'places.yaml'
    if places_file.is_file():
        names: list[str] = []
        for line in places_file.read_text(encoding='utf-8').splitlines():
            stripped = line.strip()
            if stripped.endswith(':') and not stripped.startswith('places'):
                names.append(stripped[:-1])
        phrases.update(extra_place_phrases(names))
    return phrases


def _play_wav(path: Path) -> None:
    import os
    import shutil
    import subprocess

    env = {**os.environ, 'PULSE_SERVER': os.environ.get(
        'PULSE_SERVER', 'unix:/mnt/wslg/PulseServer'
    )}
    for cmd in (
        ['paplay', str(path)],
        ['aplay', str(path)],
    ):
        if shutil.which(cmd[0]):
            subprocess.run(cmd, check=False, env=env)
            return


def main() -> int:
    """Write one WAV per phrase key."""
    parser = argparse.ArgumentParser(description='Generate robot phrase clips.')
    parser.add_argument(
        '--output',
        default=str(ROOT / 'assets' / 'phrases'),
        help='Output directory for WAV files',
    )
    parser.add_argument(
        '--profile',
        default='',
        help='TTS profile key (see --list-profiles)',
    )
    parser.add_argument('--keys', nargs='*', default=[], help='Only these keys')
    parser.add_argument(
        '--list-profiles',
        action='store_true',
        help='Print available TTS profiles and exit',
    )
    parser.add_argument(
        '--save-profile',
        action='store_true',
        help='Write chosen profile to assets/phrases/active_profile.txt',
    )
    parser.add_argument(
        '--play',
        action='store_true',
        help='Play hello.wav after generation',
    )
    args = parser.parse_args()

    if args.list_profiles:
        for profile in ROBOT_TTS_PROFILES:
            print(f'{profile.key:22} {profile.backend:6} {profile.label}')
        return 0

    profile_key = args.profile.strip() or default_profile_key()
    profile = get_profile(profile_key)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.save_profile:
        marker = out_dir / 'active_profile.txt'
        marker.write_text(profile_key + '\n', encoding='utf-8')
        print(f'Saved active profile: {profile_key} -> {marker}')

    keys = args.keys or list(_all_phrase_texts().keys())
    phrase_map = _all_phrase_texts()
    print(f'Profile: {profile.key} ({profile.label})')
    print(f'Output:  {out_dir}')
    print('')

    for key in keys:
        text = phrase_map.get(key)
        if not text:
            print(f'skip unknown key: {key}')
            continue
        dest = out_dir / f'{key}.wav'
        print(f'>>> {key}: {text!r}')
        synthesize_profile_wav(text, dest, profile_key)

    print(f'\nDone — {len(keys)} clips in {out_dir}')
    if args.play and (out_dir / 'hello.wav').is_file():
        print('Playing hello.wav ...')
        _play_wav(out_dir / 'hello.wav')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
