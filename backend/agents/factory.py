"""Factory for creating agent populations."""
from __future__ import annotations

import numpy as np

from agents.base import BaseAgent
from agents.archetypes import (
    RationalAgent, GreedyAgent, CooperativeAgent, RandomAgent, AdaptiveAgent,
)
from config import NUM_GENES, ARCHETYPE_NAMES

ARCHETYPE_MAP = {
    "rational": RationalAgent,
    "greedy": GreedyAgent,
    "cooperative": CooperativeAgent,
    "random": RandomAgent,
    "adaptive": AdaptiveAgent,
}


class AgentFactory:
    """Creates agents and populations efficiently."""

    def __init__(self, rng: np.random.Generator | None = None):
        self.rng = rng or np.random.default_rng()

    def create_agent_by_type(
        self,
        archetype: str,
        agent_id: str | None = None,
        generation: int = 0,
        strategy_genes: np.ndarray | None = None,
        location: str = "zone-0",
    ) -> BaseAgent:
        cls = ARCHETYPE_MAP.get(archetype, RandomAgent)
        genes = strategy_genes if strategy_genes is not None else self.rng.random(NUM_GENES)
        return cls(
            agent_id=agent_id,
            strategy_genes=genes,
            generation=generation,
            location=location,
            rng=self.rng,
        )

    def create_population(
        self,
        num_agents: int = 10000,
        archetype_distribution: dict[str, float] | None = None,
        zone_count: int = 4,
        generation: int = 0,
    ) -> list[BaseAgent]:
        dist = archetype_distribution or {a: 1.0 / len(ARCHETYPE_NAMES) for a in ARCHETYPE_NAMES}
        # Normalize
        total = sum(dist.values())
        dist = {k: v / total for k, v in dist.items()}

        # Pre-generate all genes in bulk (numpy vectorized)
        all_genes = self.rng.random((num_agents, NUM_GENES))
        zones = [f"zone-{i % zone_count}" for i in range(num_agents)]

        # Build archetype assignment array
        archetypes: list[str] = []
        for arch, frac in dist.items():
            count = int(num_agents * frac)
            archetypes.extend([arch] * count)
        # Fill remainder
        while len(archetypes) < num_agents:
            archetypes.append(self.rng.choice(list(dist.keys())))
        self.rng.shuffle(archetypes)  # type: ignore[arg-type]

        agents: list[BaseAgent] = []
        for i in range(num_agents):
            agent = self.create_agent_by_type(
                archetype=archetypes[i],
                agent_id=f"agent_{i:06d}",
                generation=generation,
                strategy_genes=all_genes[i],
                location=zones[i],
            )
            agents.append(agent)
        return agents
