"""WebSocket endpoint: streams tick results as JSON."""
from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.dependencies import get_registry
from api.websocket import ConnectionManager

logger = logging.getLogger("ecosim.ws")

router = APIRouter()

# Shared manager instance
ws_manager = ConnectionManager()


@router.websocket("/ws/simulations/{run_id}")
async def simulation_ws(ws: WebSocket, run_id: str):
    registry = get_registry()
    engine = registry.get(run_id)
    if engine is None:
        await ws.close(code=4004, reason="Simulation not found")
        return

    connected = await ws_manager.connect(run_id, ws)
    if not connected:
        return

    # Register a tick callback that queues results
    queue: asyncio.Queue = asyncio.Queue(maxsize=50)

    def on_tick(result):
        try:
            queue.put_nowait(result.model_dump())
        except asyncio.QueueFull:
            pass  # drop oldest-style backpressure

    engine.on_tick.append(on_tick)

    try:
        while True:
            # Send queued tick results
            try:
                data = await asyncio.wait_for(queue.get(), timeout=1.0)
                await ws.send_json(data)
            except asyncio.TimeoutError:
                # Send heartbeat ping
                try:
                    await ws.send_json({"type": "heartbeat", "run_id": run_id, "status": engine.status})
                except Exception:
                    break
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WS error: {e}")
                break
    finally:
        if on_tick in engine.on_tick:
            engine.on_tick.remove(on_tick)
        await ws_manager.disconnect(run_id, ws)
