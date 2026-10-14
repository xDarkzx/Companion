"""Unit tests for rendering result files into docs/EVALUATION.md."""
from report import render_tables, splice


def results():
    return {
        'coco_owlv2': {'metrics': {'images': 5000, 'AP': 0.41, 'AP50': 0.6, 'AP_small': 0.2,
                                   'AP_medium': 0.45, 'AP_large': 0.55,
                                   'ms_per_image_p50': 250.0},
                       'models': {'detector': 'google/owlv2@abc'}, 'device': 'RTX 5070',
                       'date': '2026-10-15', 'git_commit': 'abc1234'},
    }


def test_tables_show_each_benchmark_that_has_results():
    text = render_tables(results())
    assert '| OWLv2 | 0.410 | 0.600 | 0.200 | 0.450 | 0.550 | 250 |' in text
    assert 'eval/results/coco_owlv2.json' in text


def test_splice_replaces_only_the_generated_block():
    doc = 'intro\n<!-- results:start -->\nold\n<!-- results:end -->\noutro\n'
    assert splice(doc, 'new\n') == 'intro\n<!-- results:start -->\nnew\n<!-- results:end -->\noutro\n'
