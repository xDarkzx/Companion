"""Tests for the file-length guard. Runs under plain pytest on any OS."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_file_length import count_lines, find_violations, main  # noqa: E402


def test_counts_lines(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("a\nb\nc\n", encoding="utf-8")
    assert count_lines(sample) == 3


def test_flags_file_over_limit(tmp_path):
    big = tmp_path / "big.py"
    big.write_text("x\n" * 10, encoding="utf-8")
    violations = find_violations(tmp_path, limit=5)
    assert len(violations) == 1
    assert violations[0][0].name == "big.py"


def test_no_violations_when_under_limit(tmp_path):
    small = tmp_path / "small.py"
    small.write_text("x\n" * 3, encoding="utf-8")
    assert find_violations(tmp_path, limit=5) == []


def test_skips_build_dirs(tmp_path):
    build = tmp_path / "build"
    build.mkdir()
    (build / "generated.py").write_text("x\n" * 100, encoding="utf-8")
    assert find_violations(tmp_path, limit=5) == []


def test_ignores_non_source_files(tmp_path):
    doc = tmp_path / "notes.md"
    doc.write_text("x\n" * 100, encoding="utf-8")
    assert find_violations(tmp_path, limit=5) == []


def test_main_returns_zero_when_clean(tmp_path):
    (tmp_path / "ok.py").write_text("x\n" * 3, encoding="utf-8")
    assert main([str(tmp_path), "--limit", "5"]) == 0


def test_main_returns_one_on_violation(tmp_path):
    (tmp_path / "bad.py").write_text("x\n" * 10, encoding="utf-8")
    assert main([str(tmp_path), "--limit", "5"]) == 1
