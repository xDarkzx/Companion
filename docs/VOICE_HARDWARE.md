# Voice Hardware — mic, speaker, Whisper STT

How to add **USB voice interaction** to Companion (WonderEcho Pro, ReSpeaker, or DIY).

Related: [HUMAN_INTERFACE.md](HUMAN_INTERFACE.md) · [MEMORY_AND_RAG.md](MEMORY_AND_RAG.md) · [DEPLOY_MENTORPI.md](DEPLOY_MENTORPI.md)

---

## Important: there is no “Whisper device”

| Term | What it actually is |
|------|---------------------|
| **Whisper** | OpenAI **software** STT — runs on the **Pi 5** |
| **WonderEcho Pro** | Hiwonder **USB mic + speaker box** (MentorPi kit) |
| **Voice box** | USB audio hardware — **not** the AI model |

```
USB voice box (mic + speaker)
        ↕ ALSA
Pi 5: faster-whisper → /companion/voice_command → companion_agent
        ↕
TTS → speaker
```

---

## Recommended hardware

### Option A — MentorPi / Hiwonder ecosystem

**WonderEcho Pro** (“AI Voice Interaction Box”)

| Spec | Value |
|------|-------|
| Connection | USB Type-C |
| Mic | Noise-canceling |
| Speaker | 3W built-in |
| Chip | CI1302 (wake word) |
| Price | ~$25–70 (often bundled with robot) |
| Buy | [Hiwonder](https://www.hiwonder.com/) — ask support with order # |

Docs: [MentorPi Large AI Model course](https://docs.hiwonder.com/projects/MentorPi/en/latest/docs/15.Large_AI_Model_Course.html)

**6-Microphone Circular Array** — better far-field, no built-in speaker (add one).

---

### Option B — Open stack (best for Companion)

**[ReSpeaker XVF3800 USB 4-Mic](https://www.seeedstudio.com/)** (~$50–70)

- 4-mic array, 5 m range, beamforming, **AEC** (echo cancel)
- USB plug-and-play on Linux
- Speaker via 3.5 mm jack or JST — add 4Ω 3W speaker

Why AEC matters: robot **speaks while listening** — without echo cancellation, STT hears itself.

---

### Option C — Budget

- USB desk mic + USB mini speaker (~$20–40)
- Works for dev; poor on a moving noisy robot

---

## Software stack (Companion)

| Package | Node | Topic |
|---------|------|-------|
| `companion_voice` | `stt_node` | publishes `/companion/voice_command` |
| `companion_voice` | `tts_node` | subscribes `/companion/tts_request` |
| `companion_agent` | `agent_node` | parses → behaviors + `AgentState` |
| `companion_face` | `face_ascii_node` | cloud badge when thinking |

---

## Pi setup

```bash
bash scripts/pi_install_voice.sh
cd ros2_ws && colcon build && source install/setup.bash
```

### Find your USB device

```bash
arecord -l    # microphones
aplay -l      # speakers
```

Example output:

```
card 1: Array [ReSpeaker 4 Mic Array], device 0
```

Set in `config/voice.yaml`:

```yaml
stt_node:
  ros__parameters:
    mode: whisper
    input_device: "plughw:1,0"
tts_node:
  ros__parameters:
    output_device: "plughw:1,0"
```

---

## Launch

```bash
# Dev (type commands manually — no mic)
ros2 launch companion_bringup companion_stack.launch.py

# Pi with USB voice hardware
ros2 launch companion_bringup companion_stack.launch.py enable_voice:=true
```

Manual command (same as speaking):

```bash
ros2 topic pub /companion/voice_command std_msgs/msg/String \
  "{data: 'go to kitchen and patrol'}" --once
```

---

## STT modes (`config/voice.yaml`)

| mode | Use |
|------|-----|
| `keyboard` | Dev — publish commands via `ros2 topic pub` |
| `whisper` | Pi — faster-whisper on USB mic (3 s chunks, background thread) |
| `off` | Don't launch voice nodes |

Whisper models on Pi 5:

| Model | Speed | Accuracy |
|-------|-------|----------|
| `tiny.en` | Fastest | OK indoors |
| `base.en` | **Recommended** | Good |
| `small.en` | Slower | Better noisy rooms |

---

## TTS (Phase 3)

`tts_node` stub logs `/companion/tts_request`. Planned engines:

- **Piper** — local, fast on Pi
- **Kokoro** — natural, used in SocialRobot projects
- **EmojiVoice** — emo-style expressive speech

---

## WonderEcho Pro on MentorPi

1. Mount with USB to Pi 5
2. Default wake word: **"Hello Hiwonder"** (vendor firmware)
3. For **Whisper path**: use WonderEcho as **USB sound card** — ignore offline keywords, Pi does STT
4. Flash custom wake word via Hiwonder firmware tool (optional)

Device often appears as `ttyCH341USB*` for serial + ALSA card for audio.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No mic in `arecord -l` | Try different USB port; `lsusb` |
| Robot hears itself | Enable AEC (ReSpeaker) or lower speaker volume |
| Whisper too slow | Use `tiny.en` or Hailo for other tasks only |
| Wrong device | Set `plughw:CARD,DEV` in voice.yaml |

---

## ROS topics

| Topic | Type | Direction |
|-------|------|-----------|
| `/companion/voice_command` | `std_msgs/String` | STT → agent |
| `/companion/agent_state` | `AgentState` | agent → face |
| `/companion/tts_request` | `std_msgs/String` | agent → TTS |

---

## One sentence

**Buy a USB mic+speaker box (WonderEcho Pro or ReSpeaker), run Whisper on the Pi, plug into Companion's existing voice pipeline — no proprietary "Whisper hardware" exists.**
