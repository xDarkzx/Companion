"""Render eval/results/*.json into the tables in docs/EVALUATION.md.

Usage: python eval/report.py          rewrite the generated block
       python eval/report.py --check  fail if the document is out of date (used in CI)
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
RESULTS = REPO / 'eval' / 'results'
DOC = REPO / 'docs' / 'EVALUATION.md'
START, END = '<!-- results:start -->', '<!-- results:end -->'
NAMES = {'owlv2': 'OWLv2', 'grounding_dino': 'Grounding DINO tiny'}


def load_results(directory: Path = RESULTS) -> dict[str, dict]:
    """Every result file keyed by benchmark name."""
    return {p.stem: json.loads(p.read_text(encoding='utf-8'))
            for p in sorted(directory.glob('*.json'))}


def _fmt(value, digits: int = 3) -> str:
    return '–' if value is None else f'{value:.{digits}f}'


def _source(keys: list[str]) -> str:
    files = ', '.join(f'`eval/results/{k}.json`' for k in keys)
    return f'\nSource: {files}.\n'


def _coco(results: dict) -> str:
    keys = [k for k in results if k.startswith('coco_')]
    if not keys:
        return ''
    lines = ['### Finding named objects (COCO val2017)', '',
             '| Detector | AP | AP50 | AP small | AP medium | AP large |',
             '|---|---|---|---|---|---|']
    for key in keys:
        m = results[key]['metrics']
        name = NAMES.get(key.removeprefix('coco_'), key)
        lines.append(f"| {name} | {_fmt(m['AP'])} | {_fmt(m['AP50'])} | {_fmt(m['AP_small'])} | "
                     f"{_fmt(m['AP_medium'])} | {_fmt(m['AP_large'])} |")
    return '\n'.join(lines) + '\n' + _source(keys)


def _nyu(results: dict) -> str:
    keys = [k for k in results if k.startswith('nyu_localization_')]
    if not keys:
        return ''
    lines = ['### Placing objects in 3D (NYU Depth V2 test split)', '',
             '| Detector | Objects | Found (IoU ≥ 0.5) | Depth source | Median error | '
             'Within 10 cm | Within 25 cm |',
             '|---|---|---|---|---|---|---|']
    depth_rows = []
    for key in keys:
        m = results[key]['metrics']
        name = NAMES.get(key.removeprefix('nyu_localization_'), key)
        for label, field in (('Depth camera (raw)', 'sensor_depth'),
                             ('Monocular estimate', 'monocular_depth')):
            e = m[field]
            median = '–' if e['median_error_cm'] is None else f"{e['median_error_cm']:.1f} cm"
            lines.append(f"| {name} | {m['objects']} | {_fmt(m['detection_recall_iou50'])} | "
                         f"{label} | {median} | {_fmt(e['within_10cm'])} | "
                         f"{_fmt(e['within_25cm'])} |")
        d = m['monocular_depth_map']
        depth_rows.append(d)
    d = depth_rows[0]
    lines += ['', '### Monocular depth quality (NYU Depth V2 test split, every valid pixel)', '',
              '| AbsRel | δ < 1.25 | Median scale (truth ÷ estimate) | AbsRel after median scaling |',
              '|---|---|---|---|',
              f"| {_fmt(d['abs_rel'])} | {_fmt(d['delta1'])} | {_fmt(d['median_scale_bias'])} | "
              f"{_fmt(d['abs_rel_after_per_frame_median_scaling'])} |"]
    return '\n'.join(lines) + '\n' + _source(keys)


def render_tables(results: dict) -> str:
    """Markdown for every benchmark that has results, in a fixed order."""
    sections = [s for s in (_coco(results), _nyu(results)) if s]
    return '\n'.join(sections)


def splice(document: str, generated: str) -> str:
    """Replace the text between the results markers, leaving the rest of the document alone."""
    head, rest = document.split(START, 1)
    _old, tail = rest.split(END, 1)
    return f'{head}{START}\n{generated}{END}{tail}'


def main() -> int:
    """Rewrite or check docs/EVALUATION.md."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    current = DOC.read_text(encoding='utf-8')
    updated = splice(current, render_tables(load_results()))
    if args.check:
        if updated != current:
            print('docs/EVALUATION.md is out of date: run python eval/report.py')
            return 1
        return 0
    DOC.write_text(updated, encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())
