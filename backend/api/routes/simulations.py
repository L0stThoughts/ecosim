"""Simulation CRUD and run-control endpoints."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from models.schemas import SimulationConfig, SimulationState
from simulation.engine import SimulationEngine
from persistence.database import Database
from api.dependencies import get_registry, get_db, SimulationRegistry

router = APIRouter(prefix="/simulations", tags=["simulations"])


def _get_engine(run_id: str) -> SimulationEngine:
    registry = get_registry()
    engine = registry.get(run_id)
    if engine is None:
        raise HTTPException(status_code=404, detail=f"Simulation {run_id} not found")
    return engine


@router.post("", status_code=201)
async def create_simulation(
    config: SimulationConfig | None = None,
    db: Database = Depends(get_db),
) -> dict[str, Any]:
    cfg = config or SimulationConfig()
    engine = SimulationEngine(config=cfg)
    registry = get_registry()
    registry.add(engine)
    now = datetime.now(timezone.utc).isoformat()
    await db.save_run(
        run_id=engine.run_id,
        config=cfg.model_dump(),
        seed=engine.seed,
        status="created",
        tick_rate=cfg.tick_rate,
        max_ticks=cfg.max_ticks,
        created_at=now,
    )
    return {
        "run_id": engine.run_id,
        "status": engine.status,
        "num_agents": len(engine.agents),
        "config": cfg.model_dump(),
    }


@router.get("")
async def list_simulations() -> list[dict[str, Any]]:
    registry = get_registry()
    return [
        {
            "run_id": e.run_id,
            "status": e.status,
            "tick": e.tick,
            "alive_count": sum(1 for a in e.agents if a.alive),
            "total_agents": len(e.agents),
        }
        for e in registry.list_all()
    ]


@router.get("/{run_id}")
async def get_simulation(run_id: str) -> dict[str, Any]:
    engine = _get_engine(run_id)
    return engine.get_state()


@router.post("/{run_id}/start")
async def start_simulation(run_id: str, db: Database = Depends(get_db)) -> dict[str, str]:
    engine = _get_engine(run_id)
    if engine.status == "running":
        raise HTTPException(status_code=409, detail="Already running")
    await engine.start()
    await db.update_run_status(engine.run_id, "running", started_at=datetime.now(timezone.utc).isoformat())
    return {"run_id": run_id, "status": "running"}


@router.post("/{run_id}/pause")
async def pause_simulation(run_id: str, db: Database = Depends(get_db)) -> dict[str, str]:
    engine = _get_engine(run_id)
    await engine.pause()
    await db.update_run_status(engine.run_id, "paused")
    return {"run_id": run_id, "status": "paused"}


@router.post("/{run_id}/stop")
async def stop_simulation(run_id: str, db: Database = Depends(get_db)) -> dict[str, str]:
    engine = _get_engine(run_id)
    await engine.stop()
    await db.update_run_status(engine.run_id, "stopped", ended_at=datetime.now(timezone.utc).isoformat())
    return {"run_id": run_id, "status": "stopped"}


@router.post("/{run_id}/step")
async def step_simulation(run_id: str, n: int = 1) -> dict[str, Any]:
    engine = _get_engine(run_id)
    results = await engine.step(n=n)
    return {
        "run_id": run_id,
        "steps": n,
        "results": [r.model_dump() for r in results],
    }


@router.delete("/{run_id}", status_code=204)
async def delete_simulation(run_id: str) -> None:
    engine = _get_engine(run_id)
    if engine.status == "running":
        await engine.stop()
    registry = get_registry()
    registry.remove(run_id)
