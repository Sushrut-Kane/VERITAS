import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.db.models.attribute import Attribute, PolicyDecision
from app.db.models.audit_log import AuditEventType, AuditLog
from app.db.models.product import Product


async def list_review_queue(
    session: AsyncSession,
) -> list[tuple[Attribute, str]]:
    stmt = (
        select(Attribute, Product.sku)
        .join(Product, Attribute.product_id == Product.id)
        .where(Attribute.policy_decision == PolicyDecision.human_review)
        .order_by(Attribute.created_at.desc())
    )
    result = await session.execute(stmt)
    return [(row[0], row[1]) for row in result.all()]


async def apply_review_decision(
    session: AsyncSession,
    attribute_id: uuid.UUID,
    decision: str,
    note: str | None,
) -> Attribute:
    attribute = await session.get(Attribute, attribute_id)
    if attribute is None:
        raise NotFoundError(f"Attribute {attribute_id} not found")

    attribute.policy_decision = (
        PolicyDecision.publish if decision == "publish" else PolicyDecision.blocked
    )
    session.add(
        AuditLog(
            attribute_id=attribute.id,
            document_id=attribute.source_document_id,
            event_type=AuditEventType.human_reviewed,
            detail={"decision": decision, "note": note},
        )
    )
    await session.commit()
    await session.refresh(attribute)
    return attribute
