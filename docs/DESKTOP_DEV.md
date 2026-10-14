# Desktop dev — test on PC before Pi

**Quick start:** `bash scripts/desktop_demo.sh` from WSL (keyboard mode, face window).

Run the full **voice → agent → face → memory** loop on your computer first.
No camera, no robot, no iPhone app required.

Related: [SETUP.md](SETUP.md) · [VOICE_HARDWARE.md](VOICE_HARDWARE.md) · [HUMAN_INTERFACE.md](HUMAN_INTERFACE.md)

---

## Why PC first?

| On PC (WSL) | On Pi (later) |
|-------------|---------------|
| Fast rebuild + `colcon test` | Real motors + Nav2 |
| Pygame face window | GPIO LCD face |
| Whisper on CPU | Same stack, USB WonderEcho |
| Simulated nav (`simulated_travel_sec`) | Real `navigate_to_pose` |
| Facts in `~/.companion/facts.db` | `/var/lib/companion/facts.db` |

Deploy to Pi only after voice, memory, and face behave the way you expect.

---

## What you need

- **WSL2 + Ubuntu 24.04** with ROS 2 Jazzy ([SETUP.md](SETUP.md))
- **Windows 11 + WSLg** — pygame face window and often the default mic work out of the box
- **Microphone** — built-in laptop mic or USB headset (no camera needed)
- **Speakers** — offline voice via espeak-ng, or Piper for a neural voice (`bash scripts/desktop_install_piper.sh`)

Skip for now: depth camera, YOLO, Nav2, MentorPi vendor stack.

---

## One-command launch

```bash
# From repo root in WSL — recommended
bash scripts/desktop_demo.sh

# With USB webcam + vision preview window
bash scripts/desktop_demo.sh keyboard true

# With YOLO (after: pip3 install ultralytics && yolo download yolov8n.pt)
bash scripts/desktop_demo.sh keyboard true ~/yolov8n.pt
```

Manual launch:

```bash
cd ros2_ws
colcon build
source install/setup.bash

# Keyboard + face + memory (default)
ros2 launch companion_bringup desktop_dev.launch.py

# USB camera + detection overlay (requires ros-jazzy-usb-cam)
ros2 launch companion_bringup desktop_dev.launch.py enable_vision:=true

# Mic instead of keyboard
ros2 launch companion_bringup desktop_dev.launch.py voice_mode:=whisper
```

First Whisper run downloads the `base.en` model (~150 MB) — wait for it once.

---

## Voice

Replies are spoken with local, open-source engines only: Piper (neural, offline after
`bash scripts/desktop_install_piper.sh`) or espeak-ng. Generate the phrase clips once with
`bash scripts/robot_voice_lab.sh` and pick a profile.

## Sound effects (Emo-style bleeps)

Drop WAV/OGG files in **`~/companion/sfx/`** (preferred) or see
`companion_face/assets/sfx/README.md` for filenames (`happy.wav`, `blink.wav`, etc.).

If you have Emo source SFX, copy/rename them to match — the synth bleeps are only fallback.

## Install voice deps (WSL, one time)

```bash
bash scripts/desktop_install_deps.sh          # espeak + pygame + whisper libs
bash scripts/desktop_install_deps.sh true     # also usb_cam + ultralytics
bash scripts/desktop_download_yolo.sh         # optional YOLO weights → models/
```

List audio devices if mic is silent:

```bash
python3 -c "import sounddevice as sd; print(sd.query_devices())"
```

Set device in `config/desktop_dev.yaml` → `stt_node.input_device` (index number or `plughw:0,0`).

### WSL USB mic (only if default device fails)

On **Windows** (Admin PowerShell):

```powershell
usbipd list
usbipd bind --busid <BUSID>
usbipd attach --wsl --busid <BUSID>
```

Then in WSL: `arecord -l` and set `input_device` accordingly.

---

## Try these commands

Speak or type (keyboard mode) after the face window opens:

| Say / type | Expected |
|------------|----------|
| `remember that my favorite color is blue` | TTS/log: "Okay, I'll remember that." Cloud badge on face. |
| `what is my favorite color` | Speaks: "I remember: my favorite color is blue." Face shows retrieving. |
| `go to kitchen` | Simulated nav goal; face reacts via behaviors |
| `go to kitchen and patrol` | Nav then patrol emotion cycle |
| `stop` | Cancels plan |

Facts persist in `~/.companion/facts.db` across restarts.

Manual publish (without STT):

```bash
ros2 topic pub --once /companion/voice_command std_msgs/msg/String "{data: 'remember that dinner is at six'}"
```

---

## What runs (no camera)

```
mic/keyboard → stt_node → /companion/voice_command
                              ↓
                         agent_node ← FactStore (~/.companion/facts.db)
                              ↓
              behavior_request → behavior_controller → robot_emotion
                              ↓
                         face_ascii_node (pygame window + cloud badge)
                              ↓
                         tts_node (log or espeak)
```

**Not started:** `detector_node`, `camera_watch_node`, vision hints, Nav2.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No face window | Use Windows 11 WSLg; run from WSL terminal, not SSH |
| Whisper errors on import | `pip3 install faster-whisper sounddevice` |
| Mic picks up silence | Increase `chunk_sec` to 5–6; speak clearly after launch settles |
| "Memory storage is not configured" | Use `desktop_dev.launch.py` (sets `fact_db_path`) not bare `agent_node` |
| Robot tries to move for real | Desktop uses `simulated_travel_sec: 3.0` — safe on PC |

---

## When to move to Pi

- [ ] Remember + retrieve works on desktop
- [ ] Commands (`patrol`, `go to kitchen`, `stop`) behave correctly
- [ ] Face shows listening / retrieving / acting states
- [ ] Then: `ros2 launch companion_bringup mentorpi_deluxe.launch.py` on the Pi

Camera / follow / YOLO can wait until the voice + memory loop is solid.
