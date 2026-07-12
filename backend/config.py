"""EcoSim backend configuration defaults."""

DEFAULT_CONFIG = {
    "num_agents": 10000,
    "tick_rate": 5,
    "max_ticks": 5000,
    "seed": None,
    "snapshot_interval_ticks": 25,
    "metrics_interval_ticks": 1,
    "resource_types": ["food", "energy", "material", "currency"],
    "initial_distribution": {"food": 10000.0, "energy": 8000.0, "material": 6000.0, "currency": 15000.0},
    "regeneration_rate": {"food": 0.05, "energy": 0.03, "material": 0.02, "currency": 0.0},
    "scarcity_thresholds": {"food": 1000.0, "energy": 800.0, "material": 500.0, "currency": 0.0},
    "archetype_distribution": {
        "rational": 0.2,
        "greedy": 0.2,
        "cooperative": 0.2,
        "random": 0.2,
        "adaptive": 0.2,
    },
    "shock_probability": 0.01,
    "zone_count": 4,
    "evolution": {
        "enabled": True,
        "generation_length": 100,
        "mutation_rate": 0.05,
        "mutation_strength": 0.10,
        "crossover_rate": 0.50,
        "elitism_ratio": 0.05,
        "selection_ratio": 0.20,
        "tournament_size": 5,
    },
}

# Gene names used in strategy_genes numpy arrays
GENE_NAMES = [
    "risk_tolerance",
    "trade_aggressiveness",
    "cooperation_bias",
    "hoarding_tendency",
    "exploration_rate",
    "price_sensitivity",
    "alliance_openness",
    "resource_preference",
]
NUM_GENES = len(GENE_NAMES)

RESOURCE_TYPES = ["food", "energy", "material", "currency"]
ARCHETYPE_NAMES = ["rational", "greedy", "cooperative", "random", "adaptive"]
