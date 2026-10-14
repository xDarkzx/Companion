"""Unit tests for the evaluation helpers shared by every benchmark script."""
import json

from common import data_dir, percentile, write_result


def test_data_dir_defaults_and_can_be_overridden(monkeypatch, tmp_path):
    monkeypatch.delenv('COMPANION_DATA', raising=False)
    assert data_dir().as_posix().endswith('Datasets/companion')
    monkeypatch.setenv('COMPANION_DATA', str(tmp_path))
    assert data_dir() == tmp_path


def test_results_carry_provenance(tmp_path):
    path = write_result('demo', {'ap': 0.5}, models={'detector': 'x@abc'}, results_dir=tmp_path)
    payload = json.loads(path.read_text(encoding='utf-8'))
    assert payload['metrics'] == {'ap': 0.5}
    assert payload['models'] == {'detector': 'x@abc'}
    for key in ('benchmark', 'date', 'git_commit', 'python', 'device'):
        assert key in payload
    assert path.name == 'demo.json'


def test_percentiles():
    values = [float(v) for v in range(1, 101)]
    assert percentile(values, 50) == 50.5
    assert percentile(values, 95) == 95.05
