"""Integration fixtures: SQLite schema, an in-memory Neo4j stub, and an HTTP client.

These let the full pipeline and API run offline with no Postgres/Neo4j/LLM.
"""
import httpx
import pytest
import pytest_asyncio

from app.db import models  # noqa: F401  (register models on Base.metadata)
from app.db.base import Base
from app.db.session import engine


@pytest_asyncio.fixture(autouse=True)
async def _db_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


class InMemoryGraph:
    """Minimal stand-in for app.graph.queries backed by a Python list."""

    def __init__(self) -> None:
        self.claims: list[dict] = []
        self.agree_edges: list[tuple[str, str]] = []
        self.contradict_edges: list[tuple[str, str]] = []

    async def write_claim(self, *, sku, attr_key, claim_id, value, confidence, doc_id, filename, doc_type):
        self.claims.append(
            {
                "sku": sku,
                "attr_key": attr_key,
                "claim_id": str(claim_id),
                "value": value,
                "confidence": confidence,
            }
        )

    async def find_existing_claims_for_attribute(self, sku, attr_key, exclude_claim_id=None):
        exclude = str(exclude_claim_id) if exclude_claim_id else None
        return [
            {"claim_id": c["claim_id"], "value": c["value"], "confidence": c["confidence"]}
            for c in self.claims
            if c["sku"] == sku and c["attr_key"] == attr_key and c["claim_id"] != exclude
        ]

    async def link_claims_agree(self, claim_id_1, claim_id_2):
        self.agree_edges.append((str(claim_id_1), str(claim_id_2)))

    async def link_claims_contradict(self, claim_id_1, claim_id_2):
        self.contradict_edges.append((str(claim_id_1), str(claim_id_2)))

    async def attribute_evidence_subgraph(self, sku, attr_key):
        return {"nodes": [], "edges": []}


@pytest.fixture
def graph_store(monkeypatch):
    store = InMemoryGraph()
    from app.graph import queries

    monkeypatch.setattr(queries, "write_claim", store.write_claim)
    monkeypatch.setattr(
        queries, "find_existing_claims_for_attribute", store.find_existing_claims_for_attribute
    )
    monkeypatch.setattr(queries, "link_claims_agree", store.link_claims_agree)
    monkeypatch.setattr(queries, "link_claims_contradict", store.link_claims_contradict)
    monkeypatch.setattr(
        queries, "attribute_evidence_subgraph", store.attribute_evidence_subgraph
    )
    return store


@pytest_asyncio.fixture
async def client():
    from app.main import app

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
