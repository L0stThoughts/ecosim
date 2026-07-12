"""Request logging middleware and exception handlers."""
from __future__ import annotations

import time
import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("ecosim.api")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.monotonic()
        method = request.method
        path = request.url.path
        try:
            response = await call_next(request)
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.info(f"{method} {path} -> {response.status_code} ({elapsed_ms:.1f}ms)")
            return response
        except Exception as exc:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.error(f"{method} {path} -> 500 ({elapsed_ms:.1f}ms) {exc}")
            raise


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(KeyError)
    async def key_error_handler(request: Request, exc: KeyError):
        return JSONResponse(status_code=404, content={"detail": f"Not found: {exc}"})

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {traceback.format_exc()}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
