"""Simulation engine: tick loop, run management, async execution."""
from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

import numpy as np

from agents.base import BaseAgent
from agents.factory import AgentFactory
from simulation.world import World
from analytics.metrics import gini_coefficient, strategy_prevalence
from models.schemas import SimulationConfig, TickResult


class SimulationEngine:
    """Core simulation engine managing tick pipeline and run lifecycle."""

    def __init__(self, config: SimulationConfig | None = None, run_id: str | None = None):
        self.run_id = run_id or f"run_{uuid.uuid4().hex[:12]}"
        self.config = config or SimulationConfig()
        self.seed = self.config.seed or int(time.time() * 1000) % (2**31)
        self.rng = np.random.default_rng(self.seed)

        self.tick: int = 0
        self.generation: int = 0
        self.status: str = "created"  # created, running, paused, stopped, completed

        # World
        rp = self.config.resource_params
        self.world = World(
            zone_count=self.config.zone_count,
            resource_types=rp.resource_types,
            initial_distribution=rp.initial_distribution or None,
            regeneration_rate=rp.regeneration_rate or None,
            scarcity_thresholds=rp.scarcity_thresholds or None,
            shock_probability=self.config.shock_probability,
            rng=self.rng,
        )

        # Agents
        factory = AgentFactory(rng=self.rng)
        self.agents: list[BaseAgent] = factory.create_population(
            num_agents=self.config.num_agents,
            archetype_distribution=self.config.archetype_distribution,
            zone_count=self.config.zone_count,
        )
        self._agent_map: dict[str, BaseAgent] = {a.id: a for a in self.agents}

        # Control
        self._running = False
        self._task: asyncio.Task | None = None

        # Callbacks
        self.on_tick: list[Any] = []  # callables(tick_result)

    @property
    def alive_agents(self) -> list[BaseAgent]:
        return [a for a in self.agents if a.alive]

    def get_agent(self, agent_id: str) -> BaseAgent | None:
        return self._agent_map.get(agent_id)

    # --- Run control ---

    async def start(self) -> None:
        if self.status in ("running",):
            return
        self.status = "running"
        self._running = True
        self._task = asyncio.create_task(self._run_loop())

    async def pause(self) -> None:
        self._running = False
        self.status = "paused"

    async def stop(self) -> None:
        self._running = False
        self.status = "stopped"
        if self._task and not self._task.done():
            self._task.cancel()

    async def step(self, n: int = 1) -> list[TickResult]:
        results = []
        for _ in range(n):
            if self.tick >= self.config.max_ticks:
                self.status = "completed"
                break
            result = await self._execute_tick()
            results.append(result)
        return results

    # --- Tick loop ---

    async def _run_loop(self) -> None:
        delay = 1.0 / self.config.tick_rate if self.config.tick_rate > 0 else 0.2
        while self._running and self.tick < self.config.max_ticks:
            t0 = time.monotonic()
            await self._execute_tick()
            elapsed = time.monotonic() - t0
            sleep_time = max(0, delay - elapsed)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        if self.tick >= self.config.max_ticks:
            self.status = "completed"
        elif self._running:
            self.status = "paused"

    async def _execute_tick(self) -> TickResult:
        self.tick += 1

        # Phase 1: Environment update
        events = self.world.update(self.tick)

        # Phase 2: Agent decisions (build context once)
        context = {
            "scarcity_flags": self.world.scarcity_flags,
            "season": self.world.season,
            "tick": self.tick,
            "neighbors": [],  # simplified: no spatial neighbor lookup for perf
        }

        alive = self.alive_agents
        actions: list[tuple[BaseAgent, dict[str, Any]]] = []
        for agent in alive:
            # Provide a few random neighbor IDs for cooperative agents
            if len(alive) > 1:
                sample_size = min(5, len(alive) - 1)
                neighbor_ids = [a.id for a in self.rng.choice(alive, size=sample_size, replace=False) if a.id != agent.id]
                context["neighbors"] = neighbor_ids
            action = agent.decide(context)
            actions.append((agent, action))

        # Phase 3: Resolve actions
        for agent, action in actions:
            agent.act(action, self.world)

        # Phase 3b: Age and update wealth
        for agent in alive:
            agent.age_tick()
            agent.update_wealth()

        # Phase 4: Check generation rollover
        ep = self.config.evolution_params
        if ep.enabled and self.tick % ep.generation_length == 0:
            self.generation += 1
            events.append({
                "event_type": "generation_rollover",
                "severity": "info",
                "payload": {"generation": self.generation},
            })

        # Build result
        alive_count = sum(1 for a in self.agents if a.alive)
        dead_count = len(self.agents) - alive_count
        wealths = np.array([a.wealth for a in self.agents if a.alive])
        metrics = {
            "gini": float(gini_coefficient(wealths)) if len(wealths) > 0 else 0.0,
            "avg_wealth": float(wealths.mean()) if len(wealths) > 0 else 0.0,
            "total_wealth": float(wealths.sum()) if len(wealths) > 0 else 0.0,
            "strategy_prevalence": strategy_prevalence(self.alive_agents),
        }

        result = TickResult(
            run_id=self.run_id,
            tick=self.tick,
            generation=self.generation,
            alive_count=alive_count,
            dead_count=dead_count,
            metrics=metrics,
            events=events,
        )

        for cb in self.on_tick:
            try:
                cb(result)
            except Exception:
                pass

        return result

    def get_state(self) -> dict[str, Any]:
        alive = self.alive_agents
        archetype_counts: dict[str, int] = {}
        for a in alive:
            archetype_counts[a.archetype] = archetype_counts.get(a.archetype, 0) + 1
        return {
            "run_id": self.run_id,
            "tick": self.tick,
            "generation": self.generation,
            "status": self.status,
            "agents_summary": {
                "alive_count": len(alive),
                "dead_count": len(self.agents) - len(alive),
                "archetype_counts": archetype_counts,
            },
            "environment_state": self.world.get_state(),
        }
