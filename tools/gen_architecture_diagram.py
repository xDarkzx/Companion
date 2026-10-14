"""Generate the package graph in docs/ARCHITECTURE.md from the contract registry.

Usage: python tools/gen_architecture_diagram.py          rewrite the diagram
       python tools/gen_architecture_diagram.py --check  fail if the diagram is stale (CI)
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from companion_contracts import (  # noqa: E402
    SERVICE_CONTRACTS,
    ServiceContract,
    TOPIC_CONTRACTS,
    TopicContract,
)

DOC = Path(__file__).resolve().parents[1] / 'docs' / 'ARCHITECTURE.md'
START, END = '<!-- diagram:start -->', '<!-- diagram:end -->'


def _short(package: str) -> str:
    return package.removeprefix('companion_')


def _topic_label(topic: str) -> str:
    return topic.removeprefix('/companion/').lstrip('/')


def render_mermaid(topics: dict[str, TopicContract],
                   services: dict[str, ServiceContract]) -> str:
    """A Mermaid flowchart: packages as nodes, topics as solid edges, services dotted."""
    lines = ['```mermaid', 'flowchart LR']
    for topic in sorted(topics):
        contract = topics[topic]
        label = _topic_label(topic)
        for publisher in sorted(contract.publishers):
            if not contract.subscribers:
                lines.append(f'  {_short(publisher)} -- "{label}" --> '
                             f'out_{label.replace("/", "_")}(["{label}"])')
            for subscriber in sorted(contract.subscribers):
                lines.append(f'  {_short(publisher)} -- "{label}" --> {_short(subscriber)}')
    for name in sorted(services):
        contract = services[name]
        label = f'{_topic_label(name)} (service)'
        for client in sorted(contract.clients):
            for server in sorted(contract.servers):
                lines.append(f'  {_short(client)} -. "{label}" .-> {_short(server)}')
    lines.append('```')
    return '\n'.join(lines) + '\n'


def splice(document: str, generated: str) -> str:
    """Replace the text between the diagram markers."""
    head, rest = document.split(START, 1)
    _old, tail = rest.split(END, 1)
    return f'{head}{START}\n{generated}{END}{tail}'


def main() -> int:
    """Rewrite or check the diagram block."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    current = DOC.read_text(encoding='utf-8')
    updated = splice(current, render_mermaid(TOPIC_CONTRACTS, SERVICE_CONTRACTS))
    if args.check:
        if updated != current:
            print('docs/ARCHITECTURE.md diagram is stale: run python tools/gen_architecture_diagram.py')
            return 1
        return 0
    DOC.write_text(updated, encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())
