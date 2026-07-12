"""Agent query endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from api.dependencies import get_registry
from simulation.engine import SimulationEngine

router = APIRouter(prefix="/simulations/{run_id}/agents", tags=["agents"])


def _get_engine(run_id: str) -> SimulationEngine:
    engine = get_registry().get(run_id)
    if engine is None:
        raise HTTPException(status_code=404, detail=f"Simulation {run_id} not found")
    return engine


@router.get("")
async def list_agents(
    run_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    alive_only: bool = Query(False),
) -> dict[str, Any]:
    engine = _get_engine(run_id)
    agents = engine.agents
    if alive_only:
        agents = [a for a in agents if a.alive]
    total = len(agents)
    page = agents[offset : offset + limit]
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "agents": [a.to_dict() for a in page],
    }


@router.get("/top")
async def top_agents(
    run_id: str,
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("wealth"),
) -> list[dict[str, Any]]:
    engine = _get_engine(run_id)
    alive = [a for a in engine.agents if a.alive]
    key_fn = lambda a: getattr(a, sort_by, 0.0)
    sorted_agents = sorted(alive, key=key_fn, reverse=True)[:limit]
    return [a.to_dict() for a in sorted_agents]


@router.get("/{agent_id}")
async def get_agent(run_id: str, agent_id: str) -> dict[str, Any]:
    engine = _get_engine(run_id)
    agent = engine.get_agent(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return agent.to_dict()
