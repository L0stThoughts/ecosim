"""World environment: resource grid, scarcity, seasons, shocks, regeneration."""
from __future__ import annotations

from typing import Any
import numpy as np

from config import RESOURCE_TYPES


class World:
    """Manages the environment: zones, resources, seasons, shocks."""

    def __init__(
        self,
        zone_count: int = 4,
        resource_types: list[str] | None = None,
        initial_distribution: dict[str, float] | None = None,
        regeneration_rate: dict[str, float] | None = None,
        scarcity_thresholds: dict[str, float] | None = None,
        shock_probability: float = 0.01,
        rng: np.random.Generator | None = None,
    ):
        self.zone_count = zone_count
        self.resource_types = resource_types or RESOURCE_TYPES
        self.rng = rng or np.random.default_rng()
        self.shock_probability = shock_probability
        self.tick = 0

        init_dist = initial_distribution or {"food": 10000.0, "energy": 8000.0, "material": 6000.0, "currency": 15000.0}
        self.regen_rate = regeneration_rate or {"food": 0.05, "energy": 0.03, "material": 0.02, "currency": 0.0}
        self.scarcity_thresholds = scarcity_thresholds or {"food": 1000.0, "energy": 800.0, "material": 500.0, "currency": 0.0}

        # Resource grid: zones × resource_types as numpy array for bulk ops
        n_res = len(self.resource_types)
        self.resource_grid = np.zeros((zone_count, n_res), dtype=np.float64)
        for j, res in enumerate(self.resource_types):
            self.resource_grid[:, j] = init_dist.get(res, 1000.0) / zone_count

        self.scarcity_flags: dict[str, bool] = {r: False for r in self.resource_types}
        self.active_shocks: list[dict[str, Any]] = []
        self.seasonal_modifier: float = 1.0
        self._season_names = ["spring", "summer", "autumn", "winter"]

    @property
    def season(self) -> str:
        return self._season_names[(self.tick // 50) % 4]

    def _res_idx(self, resource: str) -> int:
        return self.resource_types.index(resource)

    def _zone_idx(self, location: str) -> int:
        try:
            return int(location.split("-")[1]) % self.zone_count
        except (IndexError, ValueError):
            return 0

    def update(self, tick: int) -> list[dict[str, Any]]:
        """Phase 1: environment update. Returns events."""
        self.tick = tick
        events: list[dict[str, Any]] = []

        # Seasonal modifier
        season = self.season
        season_mods = {"spring": 1.2, "summer": 1.0, "autumn": 0.8, "winter": 0.6}
        self.seasonal_modifier = season_mods.get(season, 1.0)

        # Regenerate resources (vectorized)
        for j, res in enumerate(self.resource_types):
            rate = self.regen_rate.get(res, 0.0) * self.seasonal_modifier
            self.resource_grid[:, j] += self.resource_grid[:, j] * rate

        # Check scarcity
        for j, res in enumerate(self.resource_types):
            total = float(self.resource_grid[:, j].sum())
            threshold = self.scarcity_thresholds.get(res, 0.0)
            self.scarcity_flags[res] = total < threshold

        # Random shocks
        if self.rng.random() < self.shock_probability:
            shock = self._generate_shock()
            self.active_shocks.append(shock)
            events.append({"event_type": "shock", "severity": "warning", "payload": shock})

        # Apply active shocks
        expired: list[int] = []
        for i, shock in enumerate(self.active_shocks):
            remaining = shock.get("duration", 0) - 1
            if remaining <= 0:
                expired.append(i)
            else:
                shock["duration"] = remaining
                self._apply_shock(shock)
        for i in reversed(expired):
            self.active_shocks.pop(i)

        return events

    def _generate_shock(self) -> dict[str, Any]:
        shock_types = ["drought", "inflation_spike", "windfall", "blight"]
        stype = self.rng.choice(shock_types)
        zone = int(self.rng.integers(0, self.zone_count))
        return {
            "shock_type": stype,
            "zone": zone,
            "magnitude": float(self.rng.uniform(0.1, 0.5)),
            "duration": int(self.rng.integers(5, 20)),
        }

    def _apply_shock(self, shock: dict[str, Any]) -> None:
        zone = shock["zone"]
        mag = shock["magnitude"]
        stype = shock["shock_type"]
        if stype == "drought":
            fi = self._res_idx("food")
            self.resource_grid[zone, fi] *= (1.0 - mag)
        elif stype == "inflation_spike":
            ci = self._res_idx("currency")
            self.resource_grid[zone, ci] *= (1.0 - mag * 0.5)
        elif stype == "windfall":
            self.resource_grid[zone, :] *= (1.0 + mag)
        elif stype == "blight":
            self.resource_grid[zone, :] *= (1.0 - mag * 0.3)

    def gather(self, location: str, resource: str, amount: float) -> float:
        """Agent gathers resource from zone. Returns actual amount gathered."""
        zi = self._zone_idx(location)
        ri = self._res_idx(resource)
        available = self.resource_grid[zi, ri]
        taken = min(amount, max(0.0, available))
        self.resource_grid[zi, ri] -= taken
        return taken

    def get_state(self) -> dict[str, Any]:
        zone_resources: dict[str, dict[str, float]] = {}
        for zi in range(self.zone_count):
            zone_resources[f"zone-{zi}"] = {
                self.resource_types[j]: float(self.resource_grid[zi, j])
                for j in range(len(self.resource_types))
            }
        return {
            "zone_resources": zone_resources,
            "scarcity_flags": dict(self.scarcity_flags),
            "active_shocks": list(self.active_shocks),
            "seasonal_modifier": self.seasonal_modifier,
            "season": self.season,
        }
