"""Bounded SQLite store for learned facts (Tier 3 RAG)."""
from __future__ import annotations

from pathlib import Path
import sqlite3


class FactStore:
    """Append-only fact memory with a fixed row cap."""

    def __init__(self, db_path: Path, max_facts: int = 500) -> None:
        """Open or create the fact database."""
        self._path = Path(db_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._max = max(1, max_facts)
        self._conn = sqlite3.connect(str(self._path), check_same_thread=False)
        self._conn.execute(
            'CREATE TABLE IF NOT EXISTS facts ('
            'id INTEGER PRIMARY KEY AUTOINCREMENT, '
            'text TEXT NOT NULL, '
            'created_at REAL NOT NULL)'
        )
        self._conn.commit()

    def add(self, text: str, created_at: float) -> None:
        """Store one fact and trim oldest rows beyond max_facts."""
        cleaned = text.strip()
        if not cleaned:
            return
        self._conn.execute(
            'INSERT INTO facts (text, created_at) VALUES (?, ?)',
            (cleaned, created_at),
        )
        self._conn.execute(
            'DELETE FROM facts WHERE id NOT IN ('
            'SELECT id FROM facts ORDER BY id DESC LIMIT ?)',
            (self._max,),
        )
        self._conn.commit()

    def search(self, query: str, limit: int = 3) -> list[str]:
        """Return facts whose text matches any query token (case-insensitive)."""
        tokens = [t for t in query.lower().split() if len(t) >= 3]
        if not tokens:
            return []
        clauses = ' OR '.join('LOWER(text) LIKE ?' for _ in tokens)
        params = [f'%{token}%' for token in tokens]
        rows = self._conn.execute(
            f'SELECT text FROM facts WHERE {clauses} ORDER BY id DESC LIMIT ?',
            (*params, limit),
        ).fetchall()
        return [row[0] for row in rows]

    def count(self) -> int:
        """Return the number of stored facts."""
        row = self._conn.execute('SELECT COUNT(*) FROM facts').fetchone()
        return int(row[0]) if row else 0

    def close(self) -> None:
        """Release the database connection."""
        self._conn.close()
