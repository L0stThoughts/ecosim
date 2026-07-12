"""Five distinct agent archetypes with unique decision logic."""
from __future__ import annotations

from typing import Any
import numpy as np

from agents.base import BaseAgent


class RationalAgent(BaseAgent):
    """Maximizes expected utility. Balances gather/trade/consume based on marginal returns."""

    def __init__(self, **kwargs):
        super().__init__(archetype="rational", **kwargs)

    def decide(self, context: dict[str, Any]) -> dict[str, Any]:
        # Find lowest resource and gather it
        if self.energy < 20:
            return {"action": "consume"}
        lowest = min(self.resources, key=lambda r: self.resources.get(r, 0.0))
        scarcity = context.get("scarcity_flags", {})
        # Avoid scarce resources (price too high), pick next best
        if scarcity.get(lowest, False) and self.gene("risk_tolerance") < 0.5:
            candidates = [r for r in self.resources if not scarcity.get(r, False)]
            if candidates:
                lowest = min(candidates, key=lambda r: self.resources.get(r, 0.0))
        return {"action": "gather", "resource": lowest}


class GreedyAgent(BaseAgent):
    """Always hoards the most valuable resource. Rarely cooperates."""

    def __init__(self, **kwargs):
        super().__init__(archetype="greedy", **kwargs)

    def decide(self, context: dict[str, Any]) -> dict[str, Any]:
        if self.energy < 15:
            return {"action": "consume"}
        # Gather currency (most valuable) or highest-scarcity resource
        scarcity = context.get("scarcity_flags", {})
        scarce = [r for r, v in scarcity.items() if v]
        target = scarce[0] if scarce else "currency"
        return {"action": "gather", "resource": target}


class CooperativeAgent(BaseAgent):
    """Prioritizes alliances and shared resource gathering."""

    def __init__(self, **kwargs):
        super().__init__(archetype="cooperative", **kwargs)

    def decide(self, context: dict[str, Any]) -> dict[str, Any]:
        if self.energy < 20:
            return {"action": "consume"}
        # Try to cooperate with nearby agents
        neighbors = context.get("neighbors", [])
        if neighbors and self._rng.random() < (0.5 + self.gene("cooperation_bias") * 0.5):
            target = self._rng.choice(neighbors) if len(neighbors) > 0 else None
            if target:
                return {"action": "cooperate", "target": target}
        # Fallback: gather food
        return {"action": "gather", "resource": "food"}


class RandomAgent(BaseAgent):
    """Picks actions uniformly at random. Useful as a baseline."""

    def __init__(self, **kwargs):
        super().__init__(archetype="random", **kwargs)

    def decide(self, context: dict[str, Any]) -> dict[str, Any]:
        if self.energy < 10:
            return {"action": "consume"}
        actions = ["gather", "idle", "consume"]
        choice = self._rng.choice(actions)
        if choice == "gather":
            resource = self._rng.choice(list(self.resources.keys()))
            return {"action": "gather", "resource": resource}
        return {"action": choice}


class AdaptiveAgent(BaseAgent):
    """Learns from past results. Shifts strategy genes toward rewarding actions."""

    def __init__(self, **kwargs):
        super().__init__(archetype="adaptive", **kwargs)
        self._last_action: str = "idle"
        self._last_wealth: float = 0.0
        self._action_scores: dict[str, float] = {"gather": 1.0, "cooperate": 1.0, "consume": 1.0, "idle": 0.5}

    def decide(self, context: dict[str, Any]) -> dict[str, Any]:
        # Update scores based on wealth delta
        delta = self.wealth - self._last_wealth
        self._action_scores[self._last_action] += delta * 0.1
        self._last_wealth = self.wealth

        if self.energy < 15:
            self._last_action = "consume"
            return {"action": "consume"}

        # Softmax-style selection weighted by scores
        actions = list(self._action_scores.keys())
        scores = np.array([max(self._action_scores[a], 0.01) for a in actions])
        probs = scores / scores.sum()
        chosen = self._rng.choice(actions, p=probs)
        self._last_action = chosen

        if chosen == "gather":
            resource = self._rng.choice(list(self.resources.keys()))
            return {"action": "gather", "resource": resource}
        if chosen == "cooperate":
            neighbors = context.get("neighbors", [])
            target = self._rng.choice(neighbors) if len(neighbors) > 0 else None
            return {"action": "cooperate", "target": target}
        return {"action": chosen}
