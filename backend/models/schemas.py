"""Pydantic schemas for EcoSim."""
from __future__ import annotations

from typing import Literal, Any
from pydantic import BaseModel, Field


ArchetypeType = Literal["rational", "greedy", "cooperative", "random", "adaptive"]


class AgentSchema(BaseModel):
    id: str
    archetype: ArchetypeType
    strategy_genes: dict[str, float] = Field(default_factory=dict)
    resources: dict[str, float] = Field(default_factory=dict)
    wealth: float = 0.0
    energy: float = 100.0
    health: float = 100.0
    age: int = 0
    generation: int = 0
    location: str = "zone-0"
    alliances: list[str] = Field(default_factory=list)
    fitness: float = 0.0
    alive: bool = True


class ResourceParams(BaseModel):
    resource_types: list[str] = Field(default_factory=lambda: ["food", "energy", "material", "currency"])
    initial_distribution: dict[str, float] = Field(default_factory=dict)
    regeneration_rate: dict[str, float] = Field(default_factory=dict)
    scarcity_thresholds: dict[str, float] = Field(default_factory=dict)


class EvolutionParams(BaseModel):
    enabled: bool = True
    generation_length: int = 100
    mutation_rate: float = 0.05
    mutation_strength: float = 0.10
    crossover_rate: float = 0.50
    elitism_ratio: float = 0.05
    selection_ratio: float = 0.20
    tournament_size: int = 5


class SimulationConfig(BaseModel):
    num_agents: int = Field(default=10000, ge=1, le=50000)
    tick_rate: int = Field(default=5, ge=1, le=120)
    max_ticks: int = Field(default=5000, ge=1)
    seed: int | None = None
    snapshot_interval_ticks: int = Field(default=25, ge=1)
    metrics_interval_ticks: int = Field(default=1, ge=1)
    resource_params: ResourceParams = Field(default_factory=ResourceParams)
    evolution_params: EvolutionParams = Field(default_factory=EvolutionParams)
    archetype_distribution: dict[str, float] = Field(
        default_factory=lambda: {"rational": 0.2, "greedy": 0.2, "cooperative": 0.2, "random": 0.2, "adaptive": 0.2}
    )
    shock_probability: float = Field(default=0.01, ge=0.0, le=1.0)
    zone_count: int = Field(default=4, ge=1)
    scenario_name: str | None = None


class SimulationState(BaseModel):
    run_id: str
    tick: int = 0
    generation: int = 0
    status: str = "created"
    agents_summary: dict[str, Any] = Field(default_factory=dict)
    environment_state: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)
    recent_events: list[dict[str, Any]] = Field(default_factory=list)
    performance: dict[str, Any] = Field(default_factory=dict)


class Transaction(BaseModel):
    id: str = ""
    run_id: str = ""
    tick: int = 0
    buyer_id: str = ""
    seller_id: str = ""
    resource: str = ""
    amount: float = 0.0
    price: float = 0.0
    zone: str | None = None
    created_at: str = ""


class RunHistory(BaseModel):
    run_id: str
    config: dict[str, Any] = Field(default_factory=dict)
    seed: int | None = None
    status: str = "created"
    start_time: str | None = None
    end_time: str | None = None
    final_metrics: dict[str, Any] = Field(default_factory=dict)
    generations: int = 0
    total_ticks: int = 0
    outcome_tags: list[str] = Field(default_factory=list)


class TickResult(BaseModel):
    run_id: str
    tick: int
    generation: int = 0
    alive_count: int = 0
    dead_count: int = 0
    metrics: dict[str, Any] = Field(default_factory=dict)
    events: list[dict[str, Any]] = Field(default_factory=list)
    transactions_count: int = 0
