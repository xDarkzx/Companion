# Robot phrase clips (pre-generated WAV)

Companion does **not** stream TTS at runtime for replies — it plays these clips (Eilik/Emo style).

## Build your voice (recommended)

```bash
bash scripts/robot_voice_lab.sh
```

1. Uses local engines only — **Piper** or **espeak-ng** — plus sox polish  
2. **Plays** each profile so you can hear them  
3. You pick a profile → generates all `hello.wav`, `happy.wav`, …  
4. Saves choice to `assets/phrases/active_profile.txt`

Skip preview, generate directly:

```bash
bash scripts/robot_voice_lab.sh espeak_chibi
bash scripts/robot_voice_lab.sh piper_amy_chibi   # offline after Piper install
```

List profiles:

```bash
python3 tools/generate_robot_phrases.py --list-profiles
```

## Keys

See `companion_voice/phrase_bank.py` — one WAV per key (`hello.wav`, `uwu.wav`, …).
