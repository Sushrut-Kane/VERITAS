"""Neo4j async driver singleton and session context manager.

Every query function opens a session through :func:`get_graph_session` — node
functions must never construct their own driver.
"""
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from neo4j import AsyncDriver, AsyncGraphDatabase, AsyncSession

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_driver: AsyncDriver | None = None

_SCHEMA_PATH = Path(__file__).parent / "schema.cypher"


def get_driver() -> AsyncDriver:
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
    return _driver


@asynccontextmanager
async def get_graph_session() -> AsyncIterator[AsyncSession]:
    async with get_driver().session() as session:
        yield session


async def close_driver() -> None:
    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None


async def apply_schema() -> None:
    """Apply constraints/indexes from schema.cypher (idempotent)."""
    statements = [
        stmt.strip()
        for stmt in _SCHEMA_PATH.read_text(encoding="utf-8").split(";")
        if stmt.strip() and not stmt.strip().startswith("//")
    ]
    async with get_graph_session() as session:
        for statement in statements:
            await session.run(statement)
    logger.info("neo4j_schema_applied", statements=len(statements))
