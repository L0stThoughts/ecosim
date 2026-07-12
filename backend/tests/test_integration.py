"""Integration tests: full simulation flow, API endpoints, database persistence."""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio
import json
import pytest
import numpy as np

from models.schemas import SimulationConfig
from simulation.engine import SimulationEngine
from evolution.genetic import GeneticAlgorithm
from analytics.metrics import gini_coefficient, wealth_distribution, strategy_prevalence
from persistence.database import Database


class TestFullSimulationFlow:
    """Create config → engine → run ticks → check metrics → evolve → run more."""

    @pytest.mark.asyncio
    async def test_full_lifecycle(self):
        cfg = SimulationConfig(num_agents=200, max_ticks=500, seed=42, zone_count=4)
        cfg.evolution_params.generation_length = 10
        engine = SimulationEngine(config=cfg)

        # Run 10 ticks
        results = await engine.step(10)
        assert len(results) == 10
        assert engine.tick == 10
        assert engine.generation == 1  # gen_length=10

        # Check metrics
        alive = engine.alive_agents
        wealths = np.array([a.wealth for a in alive])
        gini = gini_coefficient(wealths)
        assert 0 <= gini <= 1
        dist = wealth_distribution(engine.agents)
        assert dist["mean"] > 0
        prev = strategy_prevalence(engine.agents)
        assert len(prev) > 0

        # Evolve
        ga = GeneticAlgorithm(rng=np.random.default_rng(42))
        new_genes = ga.evolve_generation(engine.agents)
        assert len(new_genes) == len(engine.agents)
        # Apply new genes to agents
        for agent, genes in zip(engine.agents, new_genes):
            agent.strategy_genes = genes
            agent.alive = True
            agent.energy = 100.0

        # Run 10 more ticks
        results2 = await engine.step(10)
        assert len(results2) == 10
        assert engine.tick == 20


class TestAPIEndpoints:
    """Test API endpoints with TestClient."""

    @pytest.fixture
    async def client(self):
        from httpx import AsyncClient, ASGITransport
        from api.main import app, lifespan
        transport = ASGITransport(app=app)
        async with lifespan(app):
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                yield c

    @pytest.mark.asyncio
    async def test_health(self, client):
        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    @pytest.mark.asyncio
    async def test_create_and_list(self, client):
        r = await client.post("/api/simulations", json={"num_agents": 50, "max_ticks": 100, "seed": 1})
        assert r.status_code == 201
        data = r.json()
        run_id = data["run_id"]
        assert data["num_agents"] == 50

        r = await client.get("/api/simulations")
        assert r.status_code == 200
        sims = r.json()
        assert any(s["run_id"] == run_id for s in sims)

        r = await client.get(f"/api/simulations/{run_id}")
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_step_and_metrics(self, client):
        r = await client.post("/api/simulations", json={"num_agents": 30, "max_ticks": 50, "seed": 2})
        run_id = r.json()["run_id"]

        r = await client.post(f"/api/simulations/{run_id}/step?n=5")
        assert r.status_code == 200
        assert r.json()["steps"] == 5

        r = await client.get(f"/api/simulations/{run_id}/metrics")
        assert r.status_code == 200
        m = r.json()
        assert "gini" in m
        assert "wealth_distribution" in m

    @pytest.mark.asyncio
    async def test_agents_endpoint(self, client):
        r = await client.post("/api/simulations", json={"num_agents": 20, "seed": 3})
        run_id = r.json()["run_id"]

        r = await client.get(f"/api/simulations/{run_id}/agents?limit=10")
        assert r.status_code == 200
        assert r.json()["total"] == 20
        assert len(r.json()["agents"]) == 10

    @pytest.mark.asyncio
    async def test_404_missing_sim(self, client):
        r = await client.get("/api/simulations/nonexistent")
        assert r.status_code == 404


class TestDatabasePersistence:
    """Test save/load run via async SQLite."""

    @pytest.mark.asyncio
    async def test_save_and_load_run(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        db = Database(db_path=db_path)
        await db.connect()
        try:
            await db.save_run(
                run_id="test_run_1",
                config={"num_agents": 100},
                seed=42,
                status="created",
                created_at="2026-01-01T00:00:00Z",
            )
            row = await db.load_run("test_run_1")
            assert row is not None
            assert row["run_id"] == "test_run_1"
            assert row["seed"] == 42
            assert json.loads(row["config_json"])["num_agents"] == 100

            # Update status
            await db.update_run_status("test_run_1", "running")
            row = await db.load_run("test_run_1")
            assert row["status"] == "running"
        finally:
            await db.close()

    @pytest.mark.asyncio
    async def test_save_snapshot(self, tmp_path):
        db_path = str(tmp_path / "test2.db")
        db = Database(db_path=db_path)
        await db.connect()
        try:
            await db.save_run(run_id="r1", config={}, seed=1, created_at="now")
            await db.save_snapshot("r1", tick=5, generation=0, state_json="{}", metrics_json="{}", environment_json="{}", created_at="now")
            snaps = await db.get_snapshots("r1")
            assert len(snaps) == 1
            assert snaps[0]["tick"] == 5
        finally:
            await db.close()

    @pytest.mark.asyncio
    async def test_missing_run(self, tmp_path):
        db_path = str(tmp_path / "test3.db")
        db = Database(db_path=db_path)
        await db.connect()
        try:
            row = await db.load_run("nonexistent")
            assert row is None
        finally:
            await db.close()
