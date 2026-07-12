"""Base agent with numpy-backed strategy genes."""
from __future__ import annotations

import uuid
from typing import Any

import numpy as np

from config import GENE_NAMES, NUM_GENES, RESOURCE_TYPES


class BaseAgent:
    """Single economic agent in the simulation."""

    __slots__ = (
        "id", "archetype", "strategy_genes", "resources", "wealth",
        "energy", "health", "age", "generation", "location",
        "alliances", "fitness", "alive", "_rng",
    )

    def __init__(
        self,
        agent_id: str | None = None,
        archetype: str = "random",
        strategy_genes: np.ndarray | None = None,
        generation: int = 0,
        location: str = "zone-0",
        rng: np.random.Generator | None = None,
    ):
        self.id = agent_id or f"agent_{uuid.uuid4().hex[:12]}"
        self.archetype = archetype
        self.strategy_genes: np.ndarray = (
            strategy_genes if strategy_genes is not None
            else np.random.default_rng().random(NUM_GENES)
        )
        self.resources: dict[str, float] = {r: 10.0 for r in RESOURCE_TYPES}
        self.wealth: float = sum(self.resources.values())
        self.energy: float = 100.0
        self.health: float = 100.0
        self.age: int = 0
        self.generation: int = generation
        self.location: str = location
        self.alliances: set[str] = set()
        self.fitness: float = 0.0
        self.alive: bool = True
        self._rng = rng or np.random.default_rng()

    # Gene accessors
    def gene(self, name: str) -> float:
        idx = GENE_NAMES.index(name)
        return float(self.strategy_genes[idx])

    def decide(self, context: dict[str, Any]) -> dict[str, Any]:
        """Return an action dict. Override in subclasses."""
        return {"action": "idle"}

    def act(self, action: dict[str, Any], world: Any) -> dict[str, Any]:
        """Execute decided action against world. Returns result dict."""
        action_type = action.get("action", "idle")
        if action_type == "gather":
            resource = action.get("resource", "food")
            amount = world.gather(self.location, resource, 1.0 + self.gene("risk_tolerance"))
            self.resources[resource] = self.resources.get(resource, 0.0) + amount
            self.energy -= 5.0
            return {"gathered": amount, "resource": resource}
        elif action_type == "trade":
            return {"traded": True}
        elif action_type == "cooperate":
            target_id = action.get("target")
            if target_id:
                self.alliances.add(target_id)
            return {"alliance": target_id}
        elif action_type == "consume":
            food = min(self.resources.get("food", 0.0), 2.0)
            self.resources["food"] = self.resources.get("food", 0.0) - food
            self.energy = min(100.0, self.energy + food * 10.0)
            return {"consumed": food}
        return {"action": "idle"}

    def update_wealth(self) -> None:
        self.wealth = sum(self.resources.values())

    def age_tick(self) -> None:
        self.age += 1
        self.energy = max(0.0, self.energy - 1.0)
        if self.energy <= 0 or self.health <= 0:
            self.alive = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "archetype": self.archetype,
            "strategy_genes": {GENE_NAMES[i]: float(self.strategy_genes[i]) for i in range(NUM_GENES)},
            "resources": dict(self.resources),
            "wealth": self.wealth,
            "energy": self.energy,
            "health": self.health,
            "age": self.age,
            "generation": self.generation,
            "location": self.location,
            "alliances": list(self.alliances),
            "fitness": self.fitness,
            "alive": self.alive,
        }
