# Companion reply and sound catalog

Every line the robot **speaks** is pre-generated as a WAV. Short **beeps** play for mood and agent state (listening, thinking, errors).

## Build everything

```bash
bash scripts/robot_voice_lab.sh          # hear TTS profiles, pick one, generate all WAVs + SFX
bash scripts/robot_voice_lab.sh espeak_chibi   # skip preview
```

---

## Spoken phrases (English)

| Key | When it plays | Spoken line |
|-----|----------------|-------------|
| `hello` | Greeting | Hello! |
| `hi` | Greeting | Hi there! |
| `welcome` | Boot / intro | Hi! I'm Companion, your robot friend. |
| `how_are_you` | Boot / chat | How are you today? |
| `here_to_help` | Boot | I'm here to help. |
| `ack_ok` | Generic OK | OK. |
| `going` | Generic navigate | On my way! |
| `going_kitchen` | Go to kitchen | On my way to the kitchen. |
| `going_bedroom` | Go to bedroom | On my way to the bedroom. |
| `going_dock` | Go to dock | On my way to the dock. |
| `patrol` | Patrol command | Starting patrol. |
| `follow` | Follow command | Following you. |
| `explore` | Explore command | Going to explore. |
| `go_home` | Go home | Heading home. |
| `stop` | Stop command | Stopping now. |
| `standing_by` | Idle | Standing by. |
| `on_it` | Play with dog / quick ack | On it. |
| `remember_ok` | Stored a fact | Got it. I'll remember that. |
| `recall_lead` | Recalling memory (clip) | I remember. |
| `no_memory` | Nothing stored | I don't have that saved yet. |
| `memory_off` | No fact DB | Memory is not set up yet. |
| `dont_understand` | Unknown command | Sorry, I didn't understand that. |
| `nav_failed` | Nav2 failed | Navigation failed. |
| `yes` / `no` / `okay` | Chat | Yes. / No. / Okay. |
| `thanks` / `sorry` / `goodbye` | Chat | Thank you! / Sorry about that. / Goodbye! |
| `happy` / `sad` / `thinking` / `confused` | Emotion chat | (see `reply_catalog.py`) |

**Memory recall:** plays `recall_lead.wav` then TTS for the fact (e.g. "your favorite color is blue").

Add new places in `places.yaml` → re-run voice lab to create `going_<place>.wav`.

Source of truth: `ros2_ws/src/companion_voice/companion_voice/reply_catalog.py`

---

## Beeps and boops (not speech)

| File | When |
|------|------|
| `listen.wav` | Agent starts listening (mic on) |
| `think.wav` | Agent retrieving / thinking |
| `confirm.wav` | Agent acting on a command |
| `alert.wav` | Error / didn't understand |
| `happy.wav` / `sad.wav` / `surprise.wav` | Face emotion change |
| `blink.wav` | Eye blink |
| `yawn.wav` | Sleepy mood |
| `wake.wav` | Boot (optional) |

Download free CC0 pack:

```bash
bash scripts/fetch_robot_sfx.sh
```

Uses [Kenney Interface Sounds](https://kenney.nl/assets/interface-sounds) (CC0).

---

## User phrase → robot response

| You say | Robot speaks |
|---------|----------------|
| (boot) | hello / welcome / how_are_you |
| "go to kitchen" | On my way to the kitchen. |
| "patrol the home" | Starting patrol. |
| "stop" | Stopping now. |
| "remember that …" | Got it. I'll remember that. |
| "what is my favorite color" | I remember. + fact |
| gibberish | Sorry, I didn't understand that. |

Beeps play automatically on listen/think/error via the face node.
