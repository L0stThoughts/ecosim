"""WebSocket connection manager with backpressure."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger("ecosim.ws")

MAX_CONNECTIONS = 100


class ConnectionManager:
    """Manages WebSocket connections per simulation with backpressure."""

    def __init__(self):
        # run_id -> set of websockets
        self._connections: dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, run_id: str, ws: WebSocket) -> bool:
        """Accept and register. Returns False if at capacity."""
        total = sum(len(s) for s in self._connections.values())
        if total >= MAX_CONNECTIONS:
            await ws.close(code=1013, reason="Server at capacity")
            return False
        await ws.accept()
        async with self._lock:
            if run_id not in self._connections:
                self._connections[run_id] = set()
            self._connections[run_id].add(ws)
        logger.info(f"WS connected: {run_id} (total={total + 1})")
        return True

    async def disconnect(self, run_id: str, ws: WebSocket) -> None:
        async with self._lock:
            conns = self._connections.get(run_id)
            if conns:
                conns.discard(ws)
                if not conns:
                    del self._connections[run_id]
        logger.info(f"WS disconnected: {run_id}")

    async def broadcast(self, run_id: str, data: dict[str, Any]) -> None:
        """Send JSON to all connections for a run. Drop slow clients."""
        conns = self._connections.get(run_id)
        if not conns:
            return
        dead: list[WebSocket] = []
        for ws in list(conns):
            try:
                await asyncio.wait_for(ws.send_json(data), timeout=2.0)
            except (asyncio.TimeoutError, Exception):
                dead.append(ws)
        if dead:
            async with self._lock:
                for ws in dead:
                    conns.discard(ws)
                    try:
                        await ws.close(code=1011)
                    except Exception:
                        pass

    def connection_count(self, run_id: str | None = None) -> int:
        if run_id:
            return len(self._connections.get(run_id, set()))
        return sum(len(s) for s in self._connections.values())
