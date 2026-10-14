"""Sox post-processing presets to make neural TTS sound like a desk-pet robot."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

# sox effect chains applied after TTS render.
FX_CHAINS: dict[str, list[str]] = {
    'none': [],
    'chibi': ['pitch', '120', 'tremolo', '10', '35'],
    'robot': ['pitch', '90', 'overdrive', '4', '18', 'tremolo', '6', '45'],
    'chipmunk': ['pitch', '180'],
}


def apply_fx(source: Path, dest: Path, preset: str) -> bool:
    """Run a sox preset; copy source when sox is missing or preset is none."""
    chain = FX_CHAINS.get(preset, [])
    if not chain:
        if source != dest:
            dest.write_bytes(source.read_bytes())
        return dest.is_file()

    sox = shutil.which('sox')
    if sox is None:
        if source != dest:
            dest.write_bytes(source.read_bytes())
        return dest.is_file()

    proc = subprocess.run(
        [sox, str(source), str(dest), *chain],
        capture_output=True,
        check=False,
    )
    return proc.returncode == 0 and dest.is_file()
