# Robot sound effects (beeps, boops — not speech)

Place **WAV or OGG** files here. Download a free CC0 pack:

```bash
bash scripts/fetch_robot_sfx.sh
```

| File | When it plays |
|------|----------------|
| `listen.wav` | Agent listening (mic) |
| `think.wav` | Agent thinking / retrieving memory |
| `confirm.wav` | Agent executing a command |
| `alert.wav` | Error / didn't understand |
| `happy.wav` | Happy face emotion |
| `sad.wav` | Sad face |
| `surprise.wav` | Surprise face |
| `blink.wav` / `blink_FNZ3zVv.mp3` | Eye blink |
| `yawn.wav` | Sleepy |
| `wake.wav` | Boot (optional) |

**Speech** lives in `companion_voice/assets/phrases/` — the phrase keys are listed in `companion_voice/reply_catalog.py`.

Missing files use a simple synthesized bleep.
