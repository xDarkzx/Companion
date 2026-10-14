"""
Live webcam demo: find objects by name and show where they are.

Usage: python -m companion_vision.demo --query mug --query "water bottle" [--camera 0]
       [--video clip.mp4] [--record out.mp4] [--hfov 70] [--backend owlv2]

A webcam has no depth sensor and is usually uncalibrated, so depth comes from the monocular
model and the intrinsics from --hfov. Distances are therefore approximate (see
docs/EVALUATION.md for measured accuracy).
"""
from __future__ import annotations

import argparse
from collections.abc import Sequence

from companion_vision.types import Intrinsics, Located
import numpy as np

BOX_BGR = (120, 255, 0)
TEXT_BGR = (255, 255, 255)
LINE_PX = 2
WINDOW = 'Companion vision'


def caption(item: Located) -> str:
    """Short label for one match: name, score and distance."""
    distance = 'no depth' if item.distance is None else f'{item.distance:.1f} m'
    return f'{item.label} {item.score:.2f} | {distance}'


def draw_overlay(bgr: np.ndarray, located: Sequence[Located]) -> np.ndarray:
    """Return a copy of the frame with a box and caption for every match."""
    import cv2

    out = bgr.copy()
    for item in located:
        x0, y0, x1, y1 = (int(round(v)) for v in (item.box.x0, item.box.y0,
                                                  item.box.x1, item.box.y1))
        cv2.rectangle(out, (x0, y0), (x1, y1), BOX_BGR, LINE_PX)
        text = caption(item)
        (width, height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        top = max(0, y0 - height - 8)
        cv2.rectangle(out, (x0, top), (x0 + width + 8, top + height + 8), BOX_BGR, -1)
        cv2.putText(out, text, (x0 + 4, top + height + 3), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    (0, 0, 0), 1, cv2.LINE_AA)
    return out


def main() -> None:
    """Open the camera or video, run the finder on every frame, show and optionally record."""
    import cv2
    import torch

    from companion_vision.depth import load_depth
    from companion_vision.detector import load_detector
    from companion_vision.pipeline import Finder

    parser = argparse.ArgumentParser(description='Find objects by name in a live camera feed.')
    parser.add_argument('--query', action='append', required=True, help='object to find')
    parser.add_argument('--camera', type=int, default=0)
    parser.add_argument('--video', help='read frames from a video file instead of a camera')
    parser.add_argument('--record', help='write the annotated frames to this .mp4 file')
    parser.add_argument('--hfov', type=float, default=70.0, help='camera horizontal FOV, degrees')
    parser.add_argument('--backend', default='owlv2', choices=['owlv2', 'grounding_dino'])
    parser.add_argument('--threshold', type=float, default=0.2)
    parser.add_argument('--no-window', action='store_true', help='record without a preview')
    args = parser.parse_args()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    capture = cv2.VideoCapture(args.video if args.video else args.camera)
    ok, frame = capture.read()
    if not ok:
        raise SystemExit('could not read from the camera or video')
    height, width = frame.shape[:2]
    finder = Finder(
        load_detector(args.backend, device=device, score_threshold=args.threshold),
        load_depth('monocular', device=device),
        Intrinsics.from_fov(width, height, args.hfov),
    )
    writer = None
    if args.record:
        fps = capture.get(cv2.CAP_PROP_FPS) or 10.0
        writer = cv2.VideoWriter(args.record, cv2.VideoWriter_fourcc(*'mp4v'), fps,
                                 (width, height))
    try:
        while ok:
            located = finder.find(frame[:, :, ::-1], args.query)
            annotated = draw_overlay(frame, located)
            if writer is not None:
                writer.write(annotated)
            if not args.no_window:
                cv2.imshow(WINDOW, annotated)
                if cv2.waitKey(1) & 0xFF in (27, ord('q')):
                    break
            ok, frame = capture.read()
    finally:
        capture.release()
        if writer is not None:
            writer.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
