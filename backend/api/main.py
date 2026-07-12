"""FastAPI application entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from persistence.database import Database
from api.dependencies import SimulationRegistry, set_registry, set_db
from api.middleware import RequestLoggingMiddleware, register_exception_handlers
from api.routes import simulations, agents, analytics, config
from api.websocket.handlers import router as ws_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db = Database()
    await db.connect()
    set_db(db)

    registry = SimulationRegistry()
    set_registry(registry)

    logging.getLogger("ecosim.api").info("EcoSim API started")
    yield
    # Shutdown
    for engine in registry.list_all():
        if engine.status == "running":
            await engine.stop()
    await db.close()
    logging.getLogger("ecosim.api").info("EcoSim API stopped")


app = FastAPI(
    title="EcoSim API",
    description="Agent-based economic simulation engine",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging
app.add_middleware(RequestLoggingMiddleware)

# Exception handlers
register_exception_handlers(app)

# Mount routers
app.include_router(simulations.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(config.router, prefix="/api")
app.include_router(ws_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
