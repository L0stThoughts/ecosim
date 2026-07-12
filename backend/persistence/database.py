"""Async SQLite persistence layer."""
from __future__ import annotations

import json
from typing import Any

import aiosqlite

DB_PATH = "ecosim.db"

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'created',
    seed INTEGER,
    config_json TEXT,
    tick_rate INTEGER,
    max_ticks INTEGER,
    created_at TEXT,
    started_at TEXT,
    ended_at TEXT,
    final_metrics_json TEXT
);

CREATE TABLE IF NOT EXISTS run_snapshots (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    tick INTEGER NOT NULL,
    generation INTEGER DEFAULT 0,
    state_json TEXT,
    metrics_json TEXT,
    environment_json TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    tick INTEGER NOT NULL,
    buyer_id TEXT,
    seller_id TEXT,
    resource TEXT,
    amount REAL,
    price REAL,
    zone TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    tick INTEGER NOT NULL,
    event_type TEXT,
    severity TEXT DEFAULT 'info',
    payload_json TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS lineage (
    lineage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    child_agent_id TEXT,
    parent_a_id TEXT,
    parent_b_id TEXT,
    generation INTEGER,
    mutation_json TEXT,
    created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_snapshots_run_tick ON run_snapshots(run_id, tick);
CREATE INDEX IF NOT EXISTS idx_transactions_run_tick ON transactions(run_id, tick);
CREATE INDEX IF NOT EXISTS idx_events_run_tick ON events(run_id, tick);
CREATE INDEX IF NOT EXISTS idx_lineage_run ON lineage(run_id, generation);
"""


class Database:
    """Async SQLite database for EcoSim persistence."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._db: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self._db = await aiosqlite.connect(self.db_path)
        await self._db.executescript(CREATE_TABLES_SQL)
        await self._db.commit()

    async def close(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    async def save_run(
        self, run_id: str, config: dict, seed: int | None, status: str = "created",
        tick_rate: int = 5, max_ticks: int = 5000, created_at: str = "",
    ) -> None:
        assert self._db
        await self._db.execute(
            "INSERT OR REPLACE INTO runs (run_id, status, seed, config_json, tick_rate, max_ticks, created_at) VALUES (?,?,?,?,?,?,?)",
            (run_id, status, seed, json.dumps(config), tick_rate, max_ticks, created_at),
        )
        await self._db.commit()

    async def update_run_status(self, run_id: str, status: str, **kwargs: Any) -> None:
        assert self._db
        sets = ["status = ?"]
        vals: list[Any] = [status]
        for k, v in kwargs.items():
            sets.append(f"{k} = ?")
            vals.append(v)
        vals.append(run_id)
        await self._db.execute(f"UPDATE runs SET {', '.join(sets)} WHERE run_id = ?", vals)
        await self._db.commit()

    async def load_run(self, run_id: str) -> dict[str, Any] | None:
        assert self._db
        async with self._db.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None
            cols = [d[0] for d in cursor.description]
            return dict(zip(cols, row))

    async def save_snapshot(
        self, run_id: str, tick: int, generation: int,
        state_json: str, metrics_json: str, environment_json: str, created_at: str,
    ) -> None:
        assert self._db
        await self._db.execute(
            "INSERT INTO run_snapshots (run_id, tick, generation, state_json, metrics_json, environment_json, created_at) VALUES (?,?,?,?,?,?,?)",
            (run_id, tick, generation, state_json, metrics_json, environment_json, created_at),
        )
        await self._db.commit()

    async def save_transaction(
        self, tx_id: str, run_id: str, tick: int,
        buyer_id: str, seller_id: str, resource: str,
        amount: float, price: float, zone: str | None, created_at: str,
    ) -> None:
        assert self._db
        await self._db.execute(
            "INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?)",
            (tx_id, run_id, tick, buyer_id, seller_id, resource, amount, price, zone, created_at),
        )
        await self._db.commit()

    async def get_snapshots(self, run_id: str) -> list[dict[str, Any]]:
        assert self._db
        rows = []
        async with self._db.execute(
            "SELECT * FROM run_snapshots WHERE run_id = ? ORDER BY tick", (run_id,)
        ) as cursor:
            cols = [d[0] for d in cursor.description]
            async for row in cursor:
                rows.append(dict(zip(cols, row)))
        return rows
