# Face Preview (Phase 2 mockup)

A standalone **PC mockup** of the Companion robot face — animated WALL-E/EVE-style
anime eyes. **No ROS, no hardware** — purely to nail the *look* before we build the
real Phase 2 face node. Runs on Windows (or any desktop with Python + Pygame).

> This is a prototype. Once the look is approved, the renderer logic moves into the
> `companion_face` ROS 2 package, driven by the `RobotEmotion` topic.

## Run it

```bash
pip install pygame
python prototypes/face_preview/preview.py
```

**Controls:** `←/→` change expression · `1-9` pick · `C` eye colour ·
`D` toggle dot-matrix · `B` blink · `SPACE` auto-cycle · `ESC` quit

## See all expressions at once (no window needed)

```bash
python prototypes/face_preview/render_snapshots.py
```

Writes a PNG per expression into `prototypes/face_preview/snapshots/`.

## Files

| File | Role |
|------|------|
| `shapes.py` | Low-level glowing eye primitives (rounded eye, crescent, heart). |
| `expressions.py` | Expression definitions + animated extras (vein, tears, hearts, Zzz). |
| `face.py` | Composes a full face for an expression onto a canvas. |
| `preview.py` | Interactive desktop window. |
| `render_snapshots.py` | Headless PNG snapshot generator. |

## Expressions so far

`neutral · happy · sad · angry · cry · love · surprise · sleepy · yawn · wink`
— easy to add more (each is just a small entry in `expressions.CONFIG`).
