from __future__ import annotations

from contextlib import asynccontextmanager
import time
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.dependencies import get_trading_session_manager, get_ui_subscription_service
from app.startup import bootstrap_application, shutdown_application
from app.routers import data, health, trading, websocket
from app.utils.exceptions import XTQuantException, handle_xtquant_exception
from app.utils.helpers import format_response
from app.utils.logger import configure_logging_from_settings, log_runtime_configuration, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging_from_settings(settings)
    log_runtime_configuration("rest", settings)
    bootstrap_application(settings)
    logger.info("application startup complete")
    yield
    shutdown_application()
    try:
        get_ui_subscription_service(settings).hub.shutdown()
    except Exception as exc:
        logger.error(f"failed to shutdown subscription service: {exc}")
    try:
        get_trading_session_manager(settings).shutdown()
    except Exception as exc:
        logger.error(f"failed to shutdown trading manager: {exc}")


settings = get_settings()
app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    description="QMT xtquant gRPC-first proxy",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allow_origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = uuid.uuid4().hex[:12]
    start = time.perf_counter()
    logger.info(f"HTTP request started: id={request_id}, method={request.method}, path={request.url.path}")
    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.error(
            f"HTTP request failed: id={request_id}, method={request.method}, path={request.url.path}, duration_ms={duration_ms:.2f}, error={exc}"
        )
        raise
    duration_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    logger.info(
        f"HTTP request completed: id={request_id}, method={request.method}, path={request.url.path}, status={response.status_code}, duration_ms={duration_ms:.2f}"
    )
    return response


@app.exception_handler(XTQuantException)
async def xtquant_exception_handler(request: Request, exc: XTQuantException):
    http_exc = handle_xtquant_exception(exc)
    detail = http_exc.detail if isinstance(http_exc.detail, dict) else {"message": str(http_exc.detail)}
    return JSONResponse(
        status_code=http_exc.status_code,
        content=format_response(
            message=detail.get("message", exc.message),
            success=False,
            code=http_exc.status_code,
            data={"error_code": detail.get("error_code")} if detail.get("error_code") else None,
        ),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        detail = exc.detail.get("message", str(exc.detail))
        error_code = exc.detail.get("error_code")
    else:
        detail = str(exc.detail)
        error_code = None
    return JSONResponse(
        status_code=exc.status_code,
        content=format_response(
            message=detail,
            success=False,
            code=exc.status_code,
            data={"error_code": error_code} if error_code else None,
        ),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content=format_response(message=str(exc), success=False, code=500))


app.include_router(health.router)
app.include_router(data.router)
app.include_router(trading.router)
app.include_router(websocket.router)


@app.get("/")
async def root():
    settings = get_settings()
    return format_response(
        data={
            "name": settings.app.name,
            "version": settings.app.version,
            "mode": settings.xtquant.mode.value,
            "servers": settings.app_servers,
            "docs_url": "/docs",
        },
        message="service ready",
    )
