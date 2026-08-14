"""Service layer for attribute queries.

Provides the rich §3.5 detail response by joining Postgres data with Neo4j graph
data and audit logs.
"""
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.db.models.attribute import Attribute
from app.db.models.audit_log import AuditLog
from app.db.models.document import Document
from app.db.models.product import Product
from app.graph import queries
from app.schemas.attribute import (
    AuditLogEntry,
    AttributeDetailRead,
    ClaimRead,
    GraphEdge,
    GraphNode,
    RedTeamFindingRead,
    SourceDocumentRef,
)


async def get_attribute(session: AsyncSession, attribute_id: uuid.UUID) -> Attribute:
    attribute = await session.get(Attribute, attribute_id)
    if attribute is None:
        raise NotFoundError(f"Attribute {attribute_id} not found")
    return attribute


async def list_attributes_for_product(
    session: AsyncSession, product_id: uuid.UUID
) -> list[Attribute]:
    result = await session.execute(
        select(Attribute)
        .where(Attribute.product_id == product_id)
        .order_by(Attribute.attr_key, Attribute.created_at.desc())
    )
    return list(result.scalars().all())


async def count_sources(session: AsyncSession, attribute_id: uuid.UUID) -> int:
    """Count how many distinct source documents contributed claims for this attribute.

    For the MVP we count Attribute rows with the same product_id + attr_key as a proxy
    for source count, since each row comes from one extraction per document.
    """
    attr = await session.get(Attribute, attribute_id)
    if attr is None:
        return 0
    result = await session.execute(
        select(func.count(Attribute.id)).where(
            Attribute.product_id == attr.product_id,
            Attribute.attr_key == attr.attr_key,
        )
    )
    return result.scalar() or 1


async def get_attribute_detail(
    session: AsyncSession, attribute_id: uuid.UUID
) -> AttributeDetailRead:
    """§3.5 — build the richest response in the system.

    Joins the Attribute row with:
    - sibling Attribute rows (same product + attr_key) as claims
    - source Document metadata
    - AuditLog entries for this attribute
    - Red-team findings from the audit log detail JSON
    """
    attribute = await get_attribute(session, attribute_id)
    product = await session.get(Product, attribute.product_id)
    if product is None:
        raise NotFoundError(f"Product for attribute {attribute_id} not found")

    # ── Claims: all Attribute rows sharing the same product + attr_key ──
    sibling_result = await session.execute(
        select(Attribute)
        .where(
            Attribute.product_id == attribute.product_id,
            Attribute.attr_key == attribute.attr_key,
        )
        .order_by(Attribute.created_at)
    )
    siblings = list(sibling_result.scalars().all())

    claims: list[ClaimRead] = []
    for sib in siblings:
        doc = await session.get(Document, sib.source_document_id)
        claims.append(
            ClaimRead(
                claim_id=sib.id,
                raw_value=sib.raw_value or sib.attr_value,
                normalized_value=sib.attr_value,
                source_document=SourceDocumentRef(
                    id=doc.id if doc else sib.source_document_id,
                    filename=doc.filename if doc else "unknown",
                    doc_type=doc.doc_type.value if doc else "unknown",
                ),
                source_span=sib.source_span or "",
                extraction_confidence=sib.extraction_confidence or 0.0,
            )
        )

    # ── Audit log entries for this attribute ──
    audit_result = await session.execute(
        select(AuditLog)
        .where(AuditLog.attribute_id == attribute.id)
        .order_by(AuditLog.created_at)
    )
    audit_entries = [
        AuditLogEntry(
            event_type=log.event_type.value,
            created_at=log.created_at,
        )
        for log in audit_result.scalars().all()
    ]

    # ── Red-team findings from audit log detail JSON ──
    red_team_result = await session.execute(
        select(AuditLog)
        .where(
            AuditLog.attribute_id == attribute.id,
            AuditLog.event_type == "red_team_flagged",
        )
    )
    red_team_findings: list[RedTeamFindingRead] = []
    for log in red_team_result.scalars().all():
        findings = log.detail.get("findings", [])
        for f in findings:
            red_team_findings.append(
                RedTeamFindingRead(
                    check=f.get("check", "unknown"),
                    result=f.get("result", "unknown"),
                    detail=f.get("detail", ""),
                )
            )

    return AttributeDetailRead(
        id=attribute.id,
        attr_key=attribute.attr_key,
        attr_value=attribute.attr_value,
        classification=attribute.classification,
        classification_confidence=attribute.classification_confidence,
        reasoning=attribute.reasoning,
        policy_decision=attribute.policy_decision,
        claims=claims,
        red_team_findings=red_team_findings,
        audit_log=audit_entries,
    )


async def get_attribute_graph(
    session: AsyncSession, attribute_id: uuid.UUID
) -> dict:
    """§3.6 — reshape Neo4j subgraph to the contract format."""
    attribute = await get_attribute(session, attribute_id)
    product = await session.get(Product, attribute.product_id)
    if product is None:
        raise NotFoundError(f"Product for attribute {attribute_id} not found")

    subgraph = await queries.attribute_evidence_subgraph(product.sku, attribute.attr_key)

    # Reshape nodes from {id, labels, properties} to {id, type, label}
    nodes = []
    for n in subgraph.get("nodes", []):
        labels = n.get("labels", [])
        props = n.get("properties", {})
        node_type = labels[0] if labels else "Unknown"
        # Pick a human-readable label
        label = (
            props.get("key")
            or props.get("value")
            or props.get("filename")
            or props.get("sku")
            or node_type
        )
        nodes.append(GraphNode(id=n["id"], type=node_type, label=str(label)))

    # Edges already have {type, source, target} — map to {from, to, type}
    edges = [
        GraphEdge(source=e["source"], target=e["target"], type=e["type"])
        for e in subgraph.get("edges", [])
    ]

    return {"nodes": nodes, "edges": edges}
