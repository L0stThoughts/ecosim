"""Lineage tracking: parent→child relationships, ancestry queries."""
from __future__ import annotations

from typing import Any
from collections import defaultdict


class LineageTracker:
    """Tracks parent-child relationships across generations."""

    def __init__(self):
        # child_id -> (parent_a_id, parent_b_id, generation, mutation_info)
        self._records: list[dict[str, Any]] = []
        self._children_of: dict[str, list[str]] = defaultdict(list)
        self._parents_of: dict[str, tuple[str, str]] = {}

    def record(
        self,
        child_id: str,
        parent_a_id: str,
        parent_b_id: str,
        generation: int,
        mutation_info: dict[str, Any] | None = None,
    ) -> None:
        self._records.append({
            "child_id": child_id,
            "parent_a_id": parent_a_id,
            "parent_b_id": parent_b_id,
            "generation": generation,
            "mutation_info": mutation_info or {},
        })
        self._children_of[parent_a_id].append(child_id)
        self._children_of[parent_b_id].append(child_id)
        self._parents_of[child_id] = (parent_a_id, parent_b_id)

    def get_parents(self, agent_id: str) -> tuple[str, str] | None:
        return self._parents_of.get(agent_id)

    def get_children(self, agent_id: str) -> list[str]:
        return self._children_of.get(agent_id, [])

    def query_ancestors(self, agent_id: str, max_depth: int = 10) -> list[str]:
        """BFS up the lineage tree."""
        ancestors: list[str] = []
        queue = [agent_id]
        visited: set[str] = {agent_id}
        depth = 0
        while queue and depth < max_depth:
            next_queue: list[str] = []
            for aid in queue:
                parents = self._parents_of.get(aid)
                if parents:
                    for p in parents:
                        if p not in visited:
                            visited.add(p)
                            ancestors.append(p)
                            next_queue.append(p)
            queue = next_queue
            depth += 1
        return ancestors

    def get_generation_tree(self, generation: int) -> list[dict[str, Any]]:
        return [r for r in self._records if r["generation"] == generation]

    @property
    def all_records(self) -> list[dict[str, Any]]:
        return list(self._records)
