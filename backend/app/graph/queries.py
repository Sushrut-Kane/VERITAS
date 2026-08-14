"""All Cypher as named, fully-parameterized functions (never string-interpolate
values). Two separate functions for AGREES_WITH vs CONTRADICTS keep relationship
types static and easy to test.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from app.graph.client import get_graph_session

_WRITE_CLAIM = """
MERGE (p:Product {sku: $sku})
MERGE (a:Attribute {product_sku: $sku, key: $attr_key})
CREATE (c:Claim {id: $claim_id, value: $value, confidence: $confidence, created_at: datetime()})
MERGE (s:Source {doc_id: $doc_id}) ON CREATE SET s.filename = $filename, s.doc_type = $doc_type
MERGE (p)-[:HAS_ATTRIBUTE]->(a)
MERGE (a)-[:HAS_CLAIM]->(c)
MERGE (c)-[:EVIDENCED_BY]->(s)
"""

_FIND_EXISTING_CLAIMS = """
MATCH (:Product {sku: $sku})-[:HAS_ATTRIBUTE]->(a:Attribute {key: $attr_key})-[:HAS_CLAIM]->(c:Claim)
WHERE $exclude_claim_id IS NULL OR c.id <> $exclude_claim_id
RETURN c.id AS claim_id, c.value AS value, c.confidence AS confidence
"""

_LINK_AGREES = """
MATCH (c1:Claim {id: $claim_id_1}), (c2:Claim {id: $claim_id_2})
MERGE (c1)-[:AGREES_WITH]->(c2)
"""

_LINK_CONTRADICTS = """
MATCH (c1:Claim {id: $claim_id_1}), (c2:Claim {id: $claim_id_2})
MERGE (c1)-[:CONTRADICTS]->(c2)
"""

_EVIDENCE_SUBGRAPH = """
MATCH (a:Attribute {key: $attr_key, product_sku: $sku})-[:HAS_CLAIM]->(c:Claim)-[:EVIDENCED_BY]->(s:Source)
OPTIONAL MATCH (c)-[r:AGREES_WITH|CONTRADICTS]-(c2:Claim)
RETURN a, c, s, r, c2
"""


async def write_claim(
    *,
    sku: str,
    attr_key: str,
    claim_id: UUID | str,
    value: str,
    confidence: float | None,
    doc_id: UUID | str,
    filename: str,
    doc_type: str,
) -> None:
    async with get_graph_session() as session:
        await session.run(
            _WRITE_CLAIM,
            sku=sku,
            attr_key=attr_key,
            claim_id=str(claim_id),
            value=value,
            confidence=confidence,
            doc_id=str(doc_id),
            filename=filename,
            doc_type=doc_type,
        )


async def find_existing_claims_for_attribute(
    sku: str, attr_key: str, exclude_claim_id: UUID | str | None = None
) -> list[dict[str, Any]]:
    async with get_graph_session() as session:
        result = await session.run(
            _FIND_EXISTING_CLAIMS,
            sku=sku,
            attr_key=attr_key,
            exclude_claim_id=str(exclude_claim_id) if exclude_claim_id else None,
        )
        return [record.data() async for record in result]


async def link_claims_agree(claim_id_1: UUID | str, claim_id_2: UUID | str) -> None:
    async with get_graph_session() as session:
        await session.run(
            _LINK_AGREES, claim_id_1=str(claim_id_1), claim_id_2=str(claim_id_2)
        )


async def link_claims_contradict(claim_id_1: UUID | str, claim_id_2: UUID | str) -> None:
    async with get_graph_session() as session:
        await session.run(
            _LINK_CONTRADICTS, claim_id_1=str(claim_id_1), claim_id_2=str(claim_id_2)
        )


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if hasattr(value, "iso_format"):  # neo4j temporal types
        return value.iso_format()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _node_repr(node: Any) -> dict[str, Any]:
    return {
        "id": node.element_id,
        "labels": list(node.labels),
        "properties": _json_safe(dict(node)),
    }


async def attribute_evidence_subgraph(sku: str, attr_key: str) -> dict[str, Any]:
    """Return {"nodes": [...], "edges": [...]} for GET /attributes/{id}/graph."""
    nodes: dict[str, dict[str, Any]] = {}
    edges: set[tuple[str, str, str]] = set()

    async with get_graph_session() as session:
        result = await session.run(_EVIDENCE_SUBGRAPH, sku=sku, attr_key=attr_key)
        async for record in result:
            a, c, s = record.get("a"), record.get("c"), record.get("s")
            for node in (a, c, s, record.get("c2")):
                if node is not None:
                    rep = _node_repr(node)
                    nodes[rep["id"]] = rep
            if a is not None and c is not None:
                edges.add(("HAS_CLAIM", a.element_id, c.element_id))
            if c is not None and s is not None:
                edges.add(("EVIDENCED_BY", c.element_id, s.element_id))
            rel = record.get("r")
            if rel is not None:
                edges.add(
                    (rel.type, rel.start_node.element_id, rel.end_node.element_id)
                )

    return {
        "nodes": list(nodes.values()),
        "edges": [
            {"type": t, "source": src, "target": tgt} for (t, src, tgt) in edges
        ],
    }
