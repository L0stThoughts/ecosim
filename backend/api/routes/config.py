"""Simulation config get/put endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from models.schemas import SimulationConfig
from api.dependencies import get_registry
from simulation.engine import SimulationEngine

router = APIRouter(prefix="/simulations/{run_id}/config", tags=["config"])


def _get_engine(run_id: str) -> SimulationEngine:
    engine = get_registry().get(run_id)
    if engine is None:
        raise HTTPException(status_code=404, detail=f"Simulation {run_id} not found")
    return engine


@router.get("")
async def get_config(run_id: str) -> dict[str, Any]:
    engine = _get_engine(run_id)
    return engine.config.model_dump()


@router.put("")
async def update_config(run_id: str, config: SimulationConfig) -> dict[str, Any]:
    engine = _get_engine(run_id)
    if engine.status == "running":
        raise HTTPException(status_code=409, detail="Cannot update config while simulation is running")
    # Update mutable fields
    engine.config = config
    return {"run_id": run_id, "config": config.model_dump(), "message": "Config updated"}
