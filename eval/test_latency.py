"""Unit tests for latency summaries."""
from latency import stage_summary


def test_stage_summary_rounds_to_a_tenth_of_a_millisecond():
    assert stage_summary([10.0, 20.0, 30.0, 40.0]) == {'p50_ms': 25.0, 'p95_ms': 38.5}
