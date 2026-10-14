"""Unit tests for the scoring helpers of the NYU 3D localisation benchmark."""
from companion_vision.types import Box, Detection2D
import numpy as np
from nyu_localization import depth_metrics, greedy_match, summarize_errors
import pytest


def det(label, score, box):
    return Detection2D(label, score, box)


def test_greedy_match_pairs_best_scores_first_and_uses_each_truth_once():
    truth = [Box(0.0, 0.0, 10.0, 10.0), Box(100.0, 100.0, 110.0, 110.0)]
    preds = [det('cup', 0.4, Box(0.0, 0.0, 10.0, 10.0)),
             det('cup', 0.9, Box(1.0, 1.0, 10.0, 10.0)),
             det('cup', 0.8, Box(50.0, 50.0, 60.0, 60.0))]
    assert greedy_match(preds, truth, iou_threshold=0.5) == [(1, 0)]


def test_depth_metrics_on_a_known_error():
    gt = np.full((4, 4), 2.0)
    pred = np.full((4, 4), 2.2)
    pred[0, 0] = 4.0
    valid = np.ones((4, 4), dtype=bool)
    abs_rel, delta1 = depth_metrics(pred, gt, valid)
    assert abs_rel == pytest.approx((15 * 0.1 + 1.0) / 16)
    assert delta1 == pytest.approx(15 / 16)


def test_error_summary_reports_median_and_thresholds():
    summary = summarize_errors([0.05, 0.08, 0.2, 0.5])
    assert summary == {'objects': 4, 'median_error_cm': 14.0,
                       'within_10cm': 0.5, 'within_25cm': 0.75}


def test_error_summary_of_nothing():
    assert summarize_errors([]) == {'objects': 0, 'median_error_cm': None,
                                    'within_10cm': None, 'within_25cm': None}


def test_scale_bias_is_the_median_ratio_of_truth_to_prediction():
    from nyu_localization import scale_bias

    gt = np.full((2, 2), 3.0)
    pred = np.full((2, 2), 4.0)
    assert scale_bias(pred, gt, np.ones((2, 2), dtype=bool)) == pytest.approx(0.75)
