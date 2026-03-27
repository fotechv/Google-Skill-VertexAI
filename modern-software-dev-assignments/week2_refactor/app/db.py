from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional, Sequence

from .settings import settings


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DEFAULT_DB_PATH = DATA_DIR / "app.db"


def _db_path() -> Path:
    if settings.db_path:
        return Path(settings.db_path)
    return DEFAULT_DB_PATH


def ensure_data_directory_exists() -> None:
    _db_path().parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Context-managed SQLite connection with Row factory."""
    ensure_data_directory_exists()
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    ensure_data_directory_exists()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS action_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                text TEXT NOT NULL,
                done INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (note_id) REFERENCES notes(id)
            );
            """
        )


def insert_note(content: str) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO notes (content) VALUES (?)", (content,))
        return int(cur.lastrowid)


def get_note(note_id: int) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, content, created_at FROM notes WHERE id = ?", (note_id,))
        return cur.fetchone()


def list_notes() -> list[sqlite3.Row]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
        return list(cur.fetchall())


def insert_action_items(items: Sequence[str], note_id: Optional[int] = None) -> list[int]:
    """Insert multiple action items; returns their ids in insertion order."""
    items = [i.strip() for i in items if isinstance(i, str) and i.strip()]
    if not items:
        return []

    with get_connection() as conn:
        cur = conn.cursor()
        ids: list[int] = []
        for item in items:
            cur.execute("INSERT INTO action_items (note_id, text) VALUES (?, ?)", (note_id, item))
            ids.append(int(cur.lastrowid))
        return ids


def list_action_items(note_id: Optional[int] = None) -> list[sqlite3.Row]:
    with get_connection() as conn:
        cur = conn.cursor()
        if note_id is None:
            cur.execute("SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC")
        else:
            cur.execute(
                "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                (note_id,),
            )
        return list(cur.fetchall())


def mark_action_item_done(action_item_id: int, done: bool) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE action_items SET done = ? WHERE id = ?", (1 if done else 0, action_item_id))
