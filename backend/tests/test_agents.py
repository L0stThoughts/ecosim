"""Tests for agent archetypes: creation, decide(), act(), strategy genes."""
from __future__ import annotations

import numpy as np
import pytest

from agents.base import BaseAgent
from agents.archetypes import RationalAgent, GreedyAgent, CooperativeAgent, RandomAgent, AdaptiveAgent
from agents.factory import AgentFactory
from simulation.world import World
from config import GENE_NAMES, NUM_GENES, RESOURCE_TYPES


class TestBaseAgent:
    def test_creation_defaults(self):
        a = BaseAgent()
        assert a.archetype == "random"
        assert a.alive is True
        assert a.energy == 100.0
        assert a.health == 100.0
        assert a.age == 0
        assert len(a.strategy_genes) == NUM_GENES
        assert all(0 <= g <= 1 for g in a.strategy_genes)
        assert set(a.resources.keys()) == set(RESOURCE_TYPES)

    def test_creation_custom(self):
        genes = np.array([0.5] * NUM_GENES)
        a = BaseAgent(agent_id="custom_1", archetype="test", strategy_genes=genes, generation=3, location="zone-2")
        assert a.id == "custom_1"
        assert a.archetype == "test"
        assert a.generation == 3
        assert a.location == "zone-2"
        np.testing.assert_array_equal(a.strategy_genes, genes)

    def test_gene_accessor(self):
        genes = np.linspace(0.1, 0.8, NUM_GENES)
        a = BaseAgent(strategy_genes=genes)
        for i, name in enumerate(GENE_NAMES):
            assert abs(a.gene(name) - genes[i]) < 1e-10

    def test_decide_returns_idle(self):
        a = BaseAgent()
        assert a.decide({}) == {"action": "idle"}

    def test_act_gather(self):
        a = BaseAgent(location="zone-0")
        w = World(zone_count=4)
        result = a.act({"action": "gather", "resource": "food"}, w)
        assert "gathered" in result
        assert result["gathered"] >= 0
        assert a.energy < 100.0

    def test_act_consume(self):
        a = BaseAgent()
        a.resources["food"] = 5.0
        a.energy = 50.0
        w = World(zone_count=4)
        result = a.act({"action": "consume"}, w)
        assert result["consumed"] == 2.0
        assert a.energy > 50.0

    def test_act_cooperate(self):
        a = BaseAgent()
        w = World(zone_count=4)
        result = a.act({"action": "cooperate", "target": "agent_002"}, w)
        assert "agent_002" in a.alliances

    def test_age_tick_reduces_energy(self):
        a = BaseAgent()
        a.energy = 5.0
        a.age_tick()
        assert a.age == 1
        assert a.energy == 4.0

    def test_agent_dies_at_zero_energy(self):
        a = BaseAgent()
        a.energy = 1.0
        a.age_tick()
        assert a.energy == 0.0
        assert a.alive is False

    def test_update_wealth(self):
        a = BaseAgent()
        a.resources = {"food": 10.0, "energy": 20.0, "material": 5.0, "currency": 15.0}
        a.update_wealth()
        assert a.wealth == 50.0

    def test_to_dict(self):
        a = BaseAgent(agent_id="dict_test")
        d = a.to_dict()
        assert d["id"] == "dict_test"
        assert "strategy_genes" in d
        assert isinstance(d["strategy_genes"], dict)


class TestRationalAgent:
    def test_creation(self):
        a = RationalAgent()
        assert a.archetype == "rational"

    def test_decide_gathers_lowest_resource(self):
        a = RationalAgent()
        a.resources = {"food": 1.0, "energy": 50.0, "material": 50.0, "currency": 50.0}
        action = a.decide({"scarcity_flags": {}})
        assert action["action"] == "gather"
        assert action["resource"] == "food"

    def test_decide_consumes_when_low_energy(self):
        a = RationalAgent()
        a.energy = 10.0
        action = a.decide({"scarcity_flags": {}})
        assert action["action"] == "consume"


class TestGreedyAgent:
    def test_creation(self):
        a = GreedyAgent()
        assert a.archetype == "greedy"

    def test_decide_targets_scarce(self):
        a = GreedyAgent()
        action = a.decide({"scarcity_flags": {"food": True, "energy": False}})
        assert action["action"] == "gather"
        assert action["resource"] == "food"

    def test_decide_consumes_low_energy(self):
        a = GreedyAgent()
        a.energy = 10.0
        action = a.decide({})
        assert action["action"] == "consume"


class TestCooperativeAgent:
    def test_creation(self):
        a = CooperativeAgent()
        assert a.archetype == "cooperative"

    def test_decide_with_neighbors(self):
        rng = np.random.default_rng(0)
        genes = np.array([0.5] * NUM_GENES)
        genes[GENE_NAMES.index("cooperation_bias")] = 1.0
        a = CooperativeAgent(strategy_genes=genes, rng=rng)
        # With high cooperation_bias, should cooperate often
        actions = [a.decide({"neighbors": ["n1", "n2"]}) for _ in range(20)]
        coop_count = sum(1 for act in actions if act["action"] == "cooperate")
        assert coop_count > 0


class TestRandomAgent:
    def test_creation(self):
        a = RandomAgent()
        assert a.archetype == "random"

    def test_decide_varies(self):
        rng = np.random.default_rng(99)
        a = RandomAgent(rng=rng)
        actions = {a.decide({}).get("action") for _ in range(50)}
        assert len(actions) > 1


class TestAdaptiveAgent:
    def test_creation(self):
        a = AdaptiveAgent()
        assert a.archetype == "adaptive"

    def test_adapts_scores(self):
        rng = np.random.default_rng(7)
        a = AdaptiveAgent(rng=rng)
        a._last_wealth = 10.0
        a.wealth = 50.0  # big gain
        a._last_action = "gather"
        a.decide({"neighbors": ["x"]})
        assert a._action_scores["gather"] > 1.0


class TestAgentFactory:
    def test_create_agent_by_type(self, factory):
        for arch in ["rational", "greedy", "cooperative", "random", "adaptive"]:
            a = factory.create_agent_by_type(arch)
            assert a.archetype == arch

    def test_create_population_size(self, factory):
        pop = factory.create_population(num_agents=50)
        assert len(pop) == 50

    def test_create_population_distribution(self, factory):
        pop = factory.create_population(num_agents=100)
        archetypes = {a.archetype for a in pop}
        assert len(archetypes) == 5

    def test_create_population_unique_ids(self, factory):
        pop = factory.create_population(num_agents=100)
        ids = [a.id for a in pop]
        assert len(set(ids)) == 100
