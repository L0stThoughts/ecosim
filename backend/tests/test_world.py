"""Tests for World: resource generation, scarcity events, seasons."""
from __future__ import annotations

import numpy as np
import pytest
from simulation.world import World


class TestWorld:
    def test_creation(self, world):
        assert world.zone_count == 4
        assert world.resource_grid.shape == (4, 4)

    def test_initial_resources_positive(self, world):
        assert (world.resource_grid > 0).all()

    def test_season_cycle(self):
        w = World()
        assert w.season == "spring"  # tick 0
        w.tick = 50
        assert w.season == "summer"
        w.tick = 100
        assert w.season == "autumn"
        w.tick = 150
        assert w.season == "winter"
        w.tick = 200
        assert w.season == "spring"

    def test_update_regenerates_resources(self, world):
        initial = world.resource_grid.copy()
        world.update(1)
        # Food (col 0) should increase (regen rate > 0, spring modifier 1.2)
        assert world.resource_grid[0, 0] >= initial[0, 0]

    def test_gather_reduces_resources(self, world):
        before = world.resource_grid[0, 0]
        taken = world.gather("zone-0", "food", 5.0)
        assert taken > 0
        assert world.resource_grid[0, 0] < before

    def test_gather_limited_by_available(self, world):
        world.resource_grid[0, 0] = 1.0
        taken = world.gather("zone-0", "food", 100.0)
        assert taken == 1.0
        assert world.resource_grid[0, 0] == 0.0

    def test_scarcity_flags(self):
        w = World(zone_count=1)
        w.resource_grid[:, :] = 0.0  # deplete everything
        w.update(1)
        assert w.scarcity_flags["food"] is True
        assert w.scarcity_flags["energy"] is True
        assert w.scarcity_flags["material"] is True

    def test_shock_generation(self):
        rng = np.random.default_rng(42)
        w = World(zone_count=4, shock_probability=1.0, rng=rng)  # guaranteed shock
        events = w.update(1)
        shocks = [e for e in events if e["event_type"] == "shock"]
        assert len(shocks) > 0

    def test_no_negative_resources(self, world):
        for _ in range(100):
            world.gather("zone-0", "food", 1000.0)
        assert world.resource_grid[0, 0] >= 0.0

    def test_get_state(self, world):
        state = world.get_state()
        assert "zone_resources" in state
        assert "scarcity_flags" in state
        assert "season" in state
