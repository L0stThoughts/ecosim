"""Analytics and metrics endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
import numpy as np

from api.dependencies import get_registry
from simulation.engine import SimulationEngine
from analytics.metrics import gini_coefficient, wealth_distribution, strategy_prevalence, detect_emergent_behaviors

router = APIRouter(prefix="/simulations/{run_id}", tags=["analytics"])


def _get_engine(run_id: str) -> SimulationEngine:
    engine = get_registry().get(run_id)
    if engine is None:
        raise HTTPException(status_code=404, detail=f"Simulation {run_id} not found")
    return engine


@router.get("/metrics")
async def get_metrics(run_id: str) -> dict[str, Any]:
    engine = _get_engine(run_id)
    alive = engine.alive_agents
    wealths = np.array([a.wealth for a in alive]) if alive else np.array([])
    gini = float(gini_coefficient(wealths)) if len(wealths) > 0 else 0.0
    return {
        "run_id": run_id,
        "tick": engine.tick,
        "gini": gini,
        "wealth_distribution": wealth_distribution(engine.agents),
        "strategy_prevalence": strategy_prevalence(engine.agents),
        "emergent_behaviors": detect_emergent_behaviors(engine.agents, gini),
        "alive_count": len(alive),
        "dead_count": len(engine.agents) - len(alive),
        "environment": engine.world.get_state(),
    }


@router.get("/metrics/history")
async def get_metrics_history(run_id: str) -> dict[str, Any]:
    """Return tick-by-tick metrics from recorder snapshots (if available)."""
    recorder = get_registry().get_recorder(run_id)
    engine = _get_engine(run_id)
    snapshots = recorder.get_snapshots(run_id) if recorder else []
    return {
        "run_id": run_id,
        "current_tick": engine.tick,
        "snapshots": snapshots[-200:],  # cap response size
    }


@router.get("/transactions")
async def get_transactions(
    run_id: str,
    limit: int = Query(100, ge=1, le=1000),
    from_tick: int = Query(0, ge=0),
) -> dict[str, Any]:
    recorder = get_registry().get_recorder(run_id)
    if recorder is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    txs = recorder.get_transactions(run_id, from_tick=from_tick)
    return {
        "run_id": run_id,
        "total": len(txs),
        "transactions": [t.model_dump() for t in txs[-limit:]],
    }
