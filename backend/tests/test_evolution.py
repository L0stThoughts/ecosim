"""Tests for GeneticAlgorithm: selection, crossover, mutation, evolve_generation."""
from __future__ import annotations

import numpy as np
import pytest
from evolution.genetic import GeneticAlgorithm
from agents.factory import AgentFactory
from config import NUM_GENES


class TestGeneticAlgorithm:
    def test_fitness_eval(self, genetic_algo, small_population):
        fitness = genetic_algo.fitness_eval(small_population)
        assert len(fitness) == len(small_population)
        assert fitness.max() <= 1.0
        assert fitness.min() >= 0.0

    def test_tournament_selection(self, genetic_algo, small_population):
        fitness = genetic_algo.fitness_eval(small_population)
        selected = genetic_algo.tournament_selection(small_population, fitness, 10)
        assert len(selected) == 10
        assert all(0 <= idx < len(small_population) for idx in selected)

    def test_crossover_produces_valid_genes(self, genetic_algo):
        rng = np.random.default_rng(1)
        parent_a = rng.random(NUM_GENES)
        parent_b = rng.random(NUM_GENES)
        child1, child2 = genetic_algo.crossover(parent_a, parent_b)
        assert len(child1) == NUM_GENES
        assert len(child2) == NUM_GENES

    def test_crossover_preserves_gene_values(self, genetic_algo):
        # All genes in children come from one parent or the other
        parent_a = np.zeros(NUM_GENES)
        parent_b = np.ones(NUM_GENES)
        # Force crossover
        genetic_algo.crossover_rate = 1.0
        child1, child2 = genetic_algo.crossover(parent_a, parent_b)
        for g in child1:
            assert g == 0.0 or g == 1.0
        for g in child2:
            assert g == 0.0 or g == 1.0

    def test_mutation_stays_in_bounds(self, genetic_algo):
        genes = np.array([0.5] * NUM_GENES)
        for _ in range(100):
            mutated = genetic_algo.mutation(genes)
            assert (mutated >= 0.0).all()
            assert (mutated <= 1.0).all()

    def test_mutation_rate_zero(self):
        ga = GeneticAlgorithm(mutation_rate=0.0)
        genes = np.array([0.5] * NUM_GENES)
        mutated = ga.mutation(genes)
        np.testing.assert_array_equal(mutated, genes)

    def test_evolve_generation(self, genetic_algo, small_population):
        new_genes = genetic_algo.evolve_generation(small_population)
        assert len(new_genes) == len(small_population)
        for g in new_genes:
            assert len(g) == NUM_GENES
            assert (g >= 0.0).all()
            assert (g <= 1.0).all()

    def test_evolve_with_dead_agents(self, genetic_algo, small_population):
        # Kill half
        for a in small_population[:50]:
            a.alive = False
        new_genes = genetic_algo.evolve_generation(small_population)
        assert len(new_genes) == len(small_population)

    def test_evolve_all_dead(self, genetic_algo, small_population):
        for a in small_population:
            a.alive = False
        new_genes = genetic_algo.evolve_generation(small_population)
        assert len(new_genes) == len(small_population)
