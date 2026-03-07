import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from loguru import logger

from app.config import get_settings
from app.utils.logger import setup_logger
from app.database.session import init_db
from app.services.faiss_index import load_from_disk

from app.api.routes_health import router as health_router
from app.api.routes_chat import router as chat_router
from app.api.routes_docs import router as docs_router
from app.api.routes_history import router as history_router

settings = get_settings()

# ── Setup logger before anything else ─────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
setup_logger(debug=settings.debug)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup & shutdown events."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    await init_db()          # Create DB tables
    load_from_disk()         # Load FAISS index
    logger.info("All services ready ✓")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-style AI backend with RAG, agent orchestration, and tool routing.",
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global error handler ───────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url}: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ── Register routes ────────────────────────────────────────────────────────────
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(docs_router)
app.include_router(history_router)


@app.get("/", tags=["Root"])
async def root():
    return FileResponse("ui.html")


@app.get("/info", tags=["Root"])
async def info():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }