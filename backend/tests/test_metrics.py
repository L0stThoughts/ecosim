"""Tests for analytics: gini_coefficient, wealth_distribution, strategy_prevalence."""
from __future__ import annotations

import numpy as np
import pytest
from analytics.metrics import gini_coefficient, wealth_distribution, strategy_prevalence, detect_emergent_behaviors
from agents.base import BaseAgent


class TestGiniCoefficient:
    def test_perfect_equality(self):
        values = np.array([100.0] * 100)
        assert abs(gini_coefficient(values)) < 0.01

    def test_max_inequality(self):
        values = np.array([0.0] * 99 + [1000.0])
        g = gini_coefficient(values)
        assert g > 0.9

    def test_empty(self):
        assert gini_coefficient(np.array([])) == 0.0

    def test_all_zeros(self):
        assert gini_coefficient(np.zeros(10)) == 0.0

    def test_range_0_to_1(self):
        values = np.random.default_rng(0).random(1000) * 100
        g = gini_coefficient(values)
        assert 0 <= g <= 1


class TestWealthDistribution:
    def test_basic(self):
        agents = [BaseAgent(agent_id=f"a{i}") for i in range(20)]
        for i, a in enumerate(agents):
            a.wealth = float(i * 10)
        dist = wealth_distribution(agents)
        assert "mean" in dist
        assert "median" in dist
        assert "p50" in dist
        assert "top_10_share" in dist

    def test_empty(self):
        assert wealth_distribution([]) == {}


class TestStrategyPrevalence:
    def test_mixed(self):
        agents = []
        for arch in ["rational", "greedy", "cooperative"]:
            for i in range(10):
                a = BaseAgent(archetype=arch)
                agents.append(a)
        prev = strategy_prevalence(agents)
        assert len(prev) == 3
        assert abs(sum(prev.values()) - 1.0) < 1e-10

    def test_empty(self):
        assert strategy_prevalence([]) == {}


class TestEmergentBehaviors:
    def test_high_inequality_alert(self):
        agents = [BaseAgent() for _ in range(10)]
        alerts = detect_emergent_behaviors(agents, gini=0.7)
        types = [a["type"] for a in alerts]
        assert "high_inequality" in types

    def test_mass_extinction(self):
        agents = [BaseAgent() for _ in range(10)]
        for a in agents[:5]:
            a.alive = False
        alerts = detect_emergent_behaviors(agents, gini=0.3)
        types = [a["type"] for a in alerts]
        assert "mass_extinction" in types
