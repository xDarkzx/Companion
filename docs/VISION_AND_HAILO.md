# Vision & Hailo AI HAT+

How AI models fit the Companion stack — and what the **13 TOPS Hailo hat** does.

---

## Key idea

**AI models do not drive motors directly.**

```
Camera → Hailo YOLO → "dog at (x,y)"
              ↓
     companion_behaviors ("harass_dog"?)
              ↓
         Nav2 path plan
              ↓
      Hiwonder driver → wheels
```

| Layer | Uses ML? | Moves robot? |
|-------|----------|--------------|
| Hailo YOLO | ✅ | ❌ |
| Face emotion model | ✅ | ❌ |
| LLM / ROSA | ✅ | ❌ |
| companion_behaviors | Rules + AI inputs | ❌ |
| Nav2 | Classical algorithms | ✅ via `/cmd_vel` |
| Hiwonder driver | ❌ | ✅ |

You do **not** need Isaac Sim / Isaac Lab for a MentorPi 4-wheel car. Stock Nav2 +
lidar handles autonomy. Hailo adds **faster vision**, not driving logic.

---

## What runs where (Pi 5 + Hailo)

| Task | Hardware |
|------|----------|
| YOLO person / dog / object | **Hailo 13 TOPS** |
| Small emotion CNN | Hailo or Pi CPU |
| Nav2, SLAM, companion nodes | **Pi CPU** |
| Whisper STT | Pi CPU |
| Local LLM (Ollama) | Pi CPU |
| Motor / lidar drivers | Pi CPU |

More TOPS later = more/faster vision (multi-camera, bigger models). Navigation and
personality still live in Companion + Nav2.

---

## companion_perception (Phase 3)

Extend `detector_node` with a Hailo-backed inference path:

```
/camera/image_raw  →  Hailo runtime (.hef model)  →  /companion/detections
```

Detections feed:

- **Follow me** — person bbox → Nav2 dynamic follow (`/goal_update`)
- **Harass the dog** — `dog` class → playful follow + happy face
- **HumanEmotion** — face crop → empathy brain (MOAT)

---

## Hailo + Ubuntu note

Companion uses **Ubuntu 24.04 + Jazzy**. Hailo officially targets **Raspberry Pi OS**
first. Options when the hat arrives:

1. **Hailo Docker on Ubuntu** — camera in, ROS detections out (likely first try)
2. **CPU ONNX** — slower, fine for dev until Hailo is wired
3. Dual-boot Pi OS — avoid; keep one brain OS

Architecture unchanged regardless of which option works.

---

## Model pipeline (no training required to start)

| Model | Purpose | Training |
|-------|---------|----------|
| YOLOv8n (COCO) | person, dog, chair | Pretrained |
| Custom YOLO | your dog, your rooms | Phase 4 fine-tune |
| Face emotion | HumanEmotion msg | Pretrained or Phase 4 |
| Whisper base | STT | Pretrained |
| ROSA + LLM | free-form commands | Prompt + tools |

Phase 4: rosbag episodes → fine-tune YOLO on your home/dog.

---

## Wiring checklist (when Hailo arrives)

1. Install Hailo runtime + `hailort` on Pi
2. Compile YOLO to `.hef` via Hailo Model Zoo
3. Implement `companion_perception/hailo_detector_node.py`
4. Connect detections → `companion_behaviors` + Nav2 follow BT
5. Keep all motor control in Nav2 + vendor driver

---

## Related docs

- [HUMAN_INTERFACE.md](HUMAN_INTERFACE.md) — commands, memory, patrol
- [ENTERPRISE_STACK.md](ENTERPRISE_STACK.md) — full stack map
- [DEPLOY_MENTORPI.md](DEPLOY_MENTORPI.md) — hardware deploy
