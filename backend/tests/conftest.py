"""Shared test fixtures for EcoSim."""
from __future__ import annotations

import sys
import os

# Ensure backend root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import numpy as np

from config import GENE_NAMES, NUM_GENES, RESOURCE_TYPES
from agents.base import BaseAgent
from agents.archetypes import RationalAgent, GreedyAgent, CooperativeAgent, RandomAgent, AdaptiveAgent
from agents.factory import AgentFactory
from simulation.world import World
from simulation.engine import SimulationEngine
from evolution.genetic import GeneticAlgorithm
from models.schemas import SimulationConfig, ResourceParams, EvolutionParams


@pytest.fixture
def rng():
    return np.random.default_rng(42)


@pytest.fixture
def base_agent(rng):
    return BaseAgent(agent_id="test_agent_001", archetype="random", rng=rng)


@pytest.fixture
def small_config():
    return SimulationConfig(
        num_agents=100,
        max_ticks=200,
        tick_rate=60,
        seed=42,
        zone_count=4,
    )


@pytest.fixture
def world(rng):
    return World(zone_count=4, rng=rng)


@pytest.fixture
def factory(rng):
    return AgentFactory(rng=rng)


@pytest.fixture
def small_population(factory):
    return factory.create_population(num_agents=100, zone_count=4)


@pytest.fixture
def genetic_algo(rng):
    return GeneticAlgorithm(rng=rng)


@pytest.fixture
def engine(small_config):
    return SimulationEngine(config=small_config)
