"""Genetic algorithm: selection, crossover, mutation, evolution."""
from __future__ import annotations

import numpy as np

from agents.base import BaseAgent
from config import NUM_GENES


class GeneticAlgorithm:
    """Evolutionary operations on agent populations."""

    def __init__(
        self,
        mutation_rate: float = 0.05,
        mutation_strength: float = 0.10,
        crossover_rate: float = 0.50,
        elitism_ratio: float = 0.05,
        selection_ratio: float = 0.20,
        tournament_size: int = 5,
        rng: np.random.Generator | None = None,
    ):
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength
        self.crossover_rate = crossover_rate
        self.elitism_ratio = elitism_ratio
        self.selection_ratio = selection_ratio
        self.tournament_size = tournament_size
        self.rng = rng or np.random.default_rng()

    def fitness_eval(self, agents: list[BaseAgent]) -> np.ndarray:
        """Compute fitness for all agents. Uses wealth + survival bonus."""
        fitness = np.array([
            a.wealth + (a.age * 0.1) + (len(a.alliances) * 2.0) if a.alive else 0.0
            for a in agents
        ], dtype=np.float64)
        # Normalize
        fmax = fitness.max()
        if fmax > 0:
            fitness /= fmax
        for i, a in enumerate(agents):
            a.fitness = float(fitness[i])
        return fitness

    def tournament_selection(self, agents: list[BaseAgent], fitness: np.ndarray, n_select: int) -> list[int]:
        """Select n_select indices via tournament selection."""
        selected: list[int] = []
        n = len(agents)
        for _ in range(n_select):
            candidates = self.rng.integers(0, n, size=min(self.tournament_size, n))
            best = candidates[np.argmax(fitness[candidates])]
            selected.append(int(best))
        return selected

    def crossover(self, parent_a: np.ndarray, parent_b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Single-point crossover of two gene arrays."""
        if self.rng.random() > self.crossover_rate:
            return parent_a.copy(), parent_b.copy()
        point = int(self.rng.integers(1, NUM_GENES))
        child1 = np.concatenate([parent_a[:point], parent_b[point:]])
        child2 = np.concatenate([parent_b[:point], parent_a[point:]])
        return child1, child2

    def mutation(self, genes: np.ndarray) -> np.ndarray:
        """Apply random mutations to gene array."""
        mutated = genes.copy()
        mask = self.rng.random(NUM_GENES) < self.mutation_rate
        noise = self.rng.normal(0, self.mutation_strength, NUM_GENES)
        mutated[mask] += noise[mask]
        mutated = np.clip(mutated, 0.0, 1.0)
        return mutated

    def evolve_generation(self, agents: list[BaseAgent]) -> list[np.ndarray]:
        """Run one generation of evolution. Returns new gene arrays for offspring."""
        alive = [a for a in agents if a.alive]
        if len(alive) < 2:
            return [self.rng.random(NUM_GENES) for _ in range(len(agents))]

        fitness = self.fitness_eval(alive)
        n_total = len(agents)
        n_elite = max(1, int(n_total * self.elitism_ratio))
        n_offspring = n_total - n_elite

        # Elite: top fitness keep their genes
        elite_idx = np.argsort(fitness)[-n_elite:]
        new_genes: list[np.ndarray] = [alive[i].strategy_genes.copy() for i in elite_idx]

        # Breed offspring
        while len(new_genes) < n_total:
            parents = self.tournament_selection(alive, fitness, 2)
            child1, child2 = self.crossover(
                alive[parents[0]].strategy_genes,
                alive[parents[1]].strategy_genes,
            )
            new_genes.append(self.mutation(child1))
            if len(new_genes) < n_total:
                new_genes.append(self.mutation(child2))

        return new_genes[:n_total]
