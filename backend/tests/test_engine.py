"""Tests for SimulationEngine: create, tick, pause, resume, stop."""
from __future__ import annotations

import asyncio
import pytest
from models.schemas import SimulationConfig
from simulation.engine import SimulationEngine


@pytest.fixture
def eng():
    cfg = SimulationConfig(num_agents=50, max_ticks=100, tick_rate=60, seed=42, zone_count=2)
    return SimulationEngine(config=cfg)


class TestSimulationEngine:
    def test_creation(self, eng):
        assert eng.status == "created"
        assert eng.tick == 0
        assert len(eng.agents) == 50

    def test_run_id(self, eng):
        assert eng.run_id.startswith("run_")

    @pytest.mark.asyncio
    async def test_step_single(self, eng):
        results = await eng.step(1)
        assert len(results) == 1
        assert eng.tick == 1
        assert results[0].tick == 1

    @pytest.mark.asyncio
    async def test_step_multiple(self, eng):
        results = await eng.step(5)
        assert len(results) == 5
        assert eng.tick == 5

    @pytest.mark.asyncio
    async def test_step_respects_max_ticks(self):
        cfg = SimulationConfig(num_agents=10, max_ticks=3, seed=1)
        e = SimulationEngine(config=cfg)
        results = await e.step(10)
        assert len(results) == 3
        assert e.status == "completed"

    @pytest.mark.asyncio
    async def test_pause(self, eng):
        await eng.pause()
        assert eng.status == "paused"

    @pytest.mark.asyncio
    async def test_stop(self, eng):
        await eng.stop()
        assert eng.status == "stopped"

    @pytest.mark.asyncio
    async def test_start_and_stop(self, eng):
        await eng.start()
        assert eng.status == "running"
        await asyncio.sleep(0.1)
        await eng.stop()
        assert eng.status == "stopped"
        assert eng.tick > 0

    def test_get_state(self, eng):
        state = eng.get_state()
        assert state["run_id"] == eng.run_id
        assert "agents_summary" in state
        assert "environment_state" in state

    def test_alive_agents(self, eng):
        alive = eng.alive_agents
        assert len(alive) == 50

    @pytest.mark.asyncio
    async def test_tick_produces_metrics(self, eng):
        results = await eng.step(1)
        m = results[0].metrics
        assert "gini" in m
        assert "avg_wealth" in m
        assert "strategy_prevalence" in m

    @pytest.mark.asyncio
    async def test_generation_rollover(self):
        cfg = SimulationConfig(num_agents=20, max_ticks=200, seed=1)
        cfg.evolution_params.generation_length = 10
        e = SimulationEngine(config=cfg)
        results = await e.step(10)
        assert e.generation == 1
