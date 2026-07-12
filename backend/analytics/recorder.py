"""Transaction recorder: record trades, snapshots, query history."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from models.schemas import Transaction


class TransactionRecorder:
    """In-memory transaction and snapshot recorder."""

    def __init__(self):
        self._transactions: list[Transaction] = []
        self._snapshots: list[dict[str, Any]] = []

    def record_trade(
        self,
        run_id: str,
        tick: int,
        buyer_id: str,
        seller_id: str,
        resource: str,
        amount: float,
        price: float,
        zone: str | None = None,
    ) -> Transaction:
        tx = Transaction(
            id=f"tx_{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            tick=tick,
            buyer_id=buyer_id,
            seller_id=seller_id,
            resource=resource,
            amount=amount,
            price=price,
            zone=zone,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._transactions.append(tx)
        return tx

    def record_snapshot(self, run_id: str, tick: int, state: dict[str, Any]) -> None:
        self._snapshots.append({
            "run_id": run_id,
            "tick": tick,
            "state": state,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    def get_transactions(
        self, run_id: str, from_tick: int = 0, to_tick: int | None = None
    ) -> list[Transaction]:
        result = [t for t in self._transactions if t.run_id == run_id and t.tick >= from_tick]
        if to_tick is not None:
            result = [t for t in result if t.tick <= to_tick]
        return result

    def get_snapshots(self, run_id: str) -> list[dict[str, Any]]:
        return [s for s in self._snapshots if s["run_id"] == run_id]

    @property
    def transaction_count(self) -> int:
        return len(self._transactions)
