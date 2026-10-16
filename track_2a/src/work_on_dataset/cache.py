from dataclasses import dataclass
from typing import Literal
import json
from pathlib import Path

import sqlite3

@dataclass
class HoleScoreKey:
    id: str
    hole_src: Literal['A', 'B']
    hole_idx: int
@dataclass
class HoleScoreResult:
    tks_idx: list[int] # List of the tokens in the dataset this score refers to
    score: float # lprob of that token group


class HoleScoreCache:
    """SQLite-backed cache for completed hole scores.

    Each operation opens its own connection, so one cache instance can be used
    by multiple worker threads. SQLite's WAL mode allows readers alongside a
    writer; ``put`` replaces an existing result for the same key atomically.
    """

    def __init__(self, db_path: str | Path = Path(__file__).with_name("cache_hole_scores.sqlite3")):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("PRAGMA journal_mode = WAL")
            db.execute("""
                CREATE TABLE IF NOT EXISTS hole_scores (
                    id TEXT NOT NULL,
                    hole_src TEXT NOT NULL CHECK (hole_src IN ('A', 'B')),
                    hole_idx INTEGER NOT NULL,
                    tks_idx TEXT NOT NULL,
                    score REAL NOT NULL,
                    PRIMARY KEY (id, hole_src, hole_idx)
                )
            """)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path, timeout=30)

    @staticmethod
    def _key_values(key: HoleScoreKey) -> tuple[str, str, int]:
        if key.hole_src not in ("A", "B"):
            raise ValueError("hole_src must be 'A' or 'B'")
        return key.id, key.hole_src, key.hole_idx

    def get(self, key: HoleScoreKey) -> HoleScoreResult | None:
        """Return a cached result, or ``None`` when this key is not cached."""
        with self._connect() as db:
            row = db.execute(
                "SELECT tks_idx, score FROM hole_scores "
                "WHERE id = ? AND hole_src = ? AND hole_idx = ?",
                self._key_values(key),
            ).fetchone()
        if row is None:
            return None
        return HoleScoreResult(tks_idx=json.loads(row[0]), score=row[1])

    def put(self, key: HoleScoreKey, result: HoleScoreResult) -> None:
        """Persist a completed result, replacing any previous value for key."""
        with self._connect() as db:
            db.execute(
                "INSERT INTO hole_scores (id, hole_src, hole_idx, tks_idx, score) "
                "VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT (id, hole_src, hole_idx) DO UPDATE SET "
                "tks_idx = excluded.tks_idx, score = excluded.score",
                (*self._key_values(key), json.dumps(result.tks_idx), result.score),
            )
