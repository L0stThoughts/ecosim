"""Shared dependencies for the API layer."""
from __future__ import annotations

from typing import AsyncGenerator

from simulation.engine import SimulationEngine
from persistence.database import Database
from analytics.recorder import TransactionRecorder


class SimulationRegistry:
    """Thread-safe registry of active simulation engines."""

    def __init__(self):
        self._sims: dict[str, SimulationEngine] = {}
        self._recorders: dict[str, TransactionRecorder] = {}

    def add(self, engine: SimulationEngine) -> None:
        self._sims[engine.run_id] = engine
        self._recorders[engine.run_id] = TransactionRecorder()

    def get(self, run_id: str) -> SimulationEngine | None:
        return self._sims.get(run_id)

    def get_recorder(self, run_id: str) -> TransactionRecorder | None:
        return self._recorders.get(run_id)

    def remove(self, run_id: str) -> None:
        self._sims.pop(run_id, None)
        self._recorders.pop(run_id, None)

    def list_all(self) -> list[SimulationEngine]:
        return list(self._sims.values())

    def __len__(self) -> int:
        return len(self._sims)


# Global singletons — set during app lifespan
_registry: SimulationRegistry | None = None
_db: Database | None = None


def set_registry(reg: SimulationRegistry) -> None:
    global _registry
    _registry = reg


def get_registry() -> SimulationRegistry:
    assert _registry is not None, "SimulationRegistry not initialized"
    return _registry


def set_db(db: Database) -> None:
    global _db
    _db = db


async def get_db() -> AsyncGenerator[Database, None]:
    assert _db is not None, "Database not initialized"
    yield _db
