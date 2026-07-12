"""Tests for Pydantic models: validation, serialization."""
from __future__ import annotations

import pytest
from pydantic import ValidationError
from models.schemas import (
    AgentSchema, SimulationConfig, ResourceParams, EvolutionParams,
    TickResult, RunHistory, Transaction, SimulationState,
)


class TestSimulationConfig:
    def test_defaults(self):
        cfg = SimulationConfig()
        assert cfg.num_agents == 10000
        assert cfg.max_ticks == 5000
        assert cfg.zone_count == 4

    def test_custom(self):
        cfg = SimulationConfig(num_agents=500, max_ticks=100, seed=99)
        assert cfg.num_agents == 500
        assert cfg.seed == 99

    def test_validation_min(self):
        with pytest.raises(ValidationError):
            SimulationConfig(num_agents=0)

    def test_validation_max(self):
        with pytest.raises(ValidationError):
            SimulationConfig(num_agents=100000)

    def test_serialization(self):
        cfg = SimulationConfig(num_agents=100)
        d = cfg.model_dump()
        assert d["num_agents"] == 100
        cfg2 = SimulationConfig(**d)
        assert cfg2.num_agents == 100


class TestAgentSchema:
    def test_valid(self):
        a = AgentSchema(id="a1", archetype="rational")
        assert a.id == "a1"
        assert a.alive is True

    def test_invalid_archetype(self):
        with pytest.raises(ValidationError):
            AgentSchema(id="a1", archetype="invalid_type")

    def test_roundtrip(self):
        a = AgentSchema(id="a1", archetype="greedy", wealth=42.0)
        d = a.model_dump()
        a2 = AgentSchema(**d)
        assert a2.wealth == 42.0


class TestTickResult:
    def test_create(self):
        tr = TickResult(run_id="r1", tick=5, alive_count=100, dead_count=10)
        assert tr.tick == 5

    def test_serialize(self):
        tr = TickResult(run_id="r1", tick=1)
        d = tr.model_dump()
        assert d["run_id"] == "r1"


class TestEvolutionParams:
    def test_defaults(self):
        ep = EvolutionParams()
        assert ep.enabled is True
        assert ep.mutation_rate == 0.05


class TestTransaction:
    def test_create(self):
        t = Transaction(id="tx1", run_id="r1", tick=10, resource="food", amount=5.0, price=2.0)
        assert t.amount == 5.0
