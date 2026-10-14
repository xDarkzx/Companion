"""Tests for the face GIF renderer used for README media."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from render_face_gif import FPS, storyboard  # noqa: E402


def test_storyboard_follows_a_find_request_then_shows_the_moods():
    moods = [shot.mood for shot in storyboard()]
    assert moods[:3] == ['neutral', 'surprise', 'happy']
    assert {'sad', 'love', 'angry', 'sleepy'} <= set(moods)


def test_the_search_shot_shows_the_status_line_and_cloud_badge():
    search = storyboard()[1]
    assert search.cloud and search.status.startswith('looking for')


def test_rendered_frames_are_not_blank():
    pytest.importorskip('pygame')
    pytest.importorskip('PIL')
    from render_face_gif import render_frames

    frames = render_frames(storyboard()[:1])
    assert len(frames) == round(storyboard()[0].seconds * FPS)
    assert frames[0].getbbox() is not None
