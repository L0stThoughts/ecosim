"""Analytics metrics: gini, wealth distribution, strategy prevalence, emergent behaviors."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from agents.base import BaseAgent


def gini_coefficient(values: np.ndarray) -> float:
    """Compute Gini coefficient from an array of values. 0=perfect equality, 1=max inequality."""
    if len(values) == 0:
        return 0.0
    values = np.sort(values)
    n = len(values)
    total = values.sum()
    if total == 0:
        return 0.0
    index = np.arange(1, n + 1)
    return float((2.0 * (index * values).sum() / (n * total)) - (n + 1.0) / n)


def wealth_distribution(agents: list[BaseAgent], percentiles: list[int] | None = None) -> dict[str, float]:
    """Return wealth distribution stats."""
    if not agents:
        return {}
    wealths = np.array([a.wealth for a in agents if a.alive])
    if len(wealths) == 0:
        return {}
    pcts = percentiles or [10, 25, 50, 75, 90]
    result: dict[str, float] = {
        "mean": float(wealths.mean()),
        "median": float(np.median(wealths)),
        "std": float(wealths.std()),
        "min": float(wealths.min()),
        "max": float(wealths.max()),
        "total": float(wealths.sum()),
    }
    for p in pcts:
        result[f"p{p}"] = float(np.percentile(wealths, p))
    # Top 10% share
    sorted_w = np.sort(wealths)
    top10_idx = int(len(sorted_w) * 0.9)
    total = sorted_w.sum()
    if total > 0:
        result["top_10_share"] = float(sorted_w[top10_idx:].sum() / total)
    return result


def strategy_prevalence(agents: list[BaseAgent]) -> dict[str, float]:
    """Return fraction of alive agents per archetype."""
    alive = [a for a in agents if a.alive]
    if not alive:
        return {}
    counts: dict[str, int] = {}
    for a in alive:
        counts[a.archetype] = counts.get(a.archetype, 0) + 1
    n = len(alive)
    return {k: v / n for k, v in counts.items()}


def detect_emergent_behaviors(
    agents: list[BaseAgent],
    gini: float,
    prev_gini: float | None = None,
) -> list[dict[str, Any]]:
    """Detect notable emergent patterns."""
    alerts: list[dict[str, Any]] = []

    # High inequality
    if gini > 0.6:
        alerts.append({"type": "high_inequality", "severity": "warning", "gini": gini})

    # Rapid inequality change
    if prev_gini is not None and abs(gini - prev_gini) > 0.1:
        alerts.append({"type": "inequality_acceleration", "severity": "warning", "delta": gini - prev_gini})

    # Monopoly detection: single archetype > 50%
    prev = strategy_prevalence(agents)
    for arch, frac in prev.items():
        if frac > 0.5:
            alerts.append({"type": "archetype_dominance", "severity": "info", "archetype": arch, "share": frac})

    # Mass extinction: >30% dead
    total = len(agents)
    dead = sum(1 for a in agents if not a.alive)
    if total > 0 and dead / total > 0.3:
        alerts.append({"type": "mass_extinction", "severity": "critical", "death_rate": dead / total})

    return alerts
