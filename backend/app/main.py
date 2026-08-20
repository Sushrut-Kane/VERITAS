"""FastAPI application factory."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import (
    attributes,
    auth,
    catalog,
    delivery,
    documents,
    pipeline_status,
    products,
    review,
)
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.graph.client import apply_schema, close_driver

logger = get_logger(__name__)

_ROUTERS = (
    auth,
    products,
    documents,
    attributes,
    review,
    catalog,
    pipeline_status,
    delivery,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    Path(settings.storage_dir).mkdir(parents=True, exist_ok=True)
    try:
        await apply_schema()
    except Exception as exc:  # don't block startup if Neo4j isn't up yet
        logger.warning("neo4j_schema_setup_failed", error=str(exc))
    yield
    await close_driver()


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="VERITAS API", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)

    for module in _ROUTERS:
        app.include_router(module.router)

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment}

    return app


app = create_app()
