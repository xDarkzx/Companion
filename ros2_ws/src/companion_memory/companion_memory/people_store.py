"""Load known people names (face/voice IDs arrive in Phase 3)."""
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class PersonRecord:
    """A person Companion can greet by name."""

    name: str
    note: str = ''


def load_people(path: Path) -> dict[str, PersonRecord]:
    """Parse people.yaml into a name lookup."""
    if not path.is_file():
        return {}

    raw = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    people_block = raw.get('people', {})
    result: dict[str, PersonRecord] = {}
    for name, info in people_block.items():
        note = ''
        if isinstance(info, dict):
            note = str(info.get('note', ''))
        result[name.strip().lower()] = PersonRecord(
            name=name.strip().lower(),
            note=note,
        )
    return result
