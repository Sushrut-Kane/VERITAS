"""Service layer for review operations (§3.7, §3.8)."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.db.models.attribute import Attribute, Classification, PolicyDecision
from app.db.models.audit_log import AuditEventType, AuditLog
from app.db.models.product import Product
from app.schemas.attribute import AttributeDetailRead
from app.services import attribute_service


async def list_review_queue(
    session: AsyncSession,
) -> list[tuple[Attribute, str]]:
    """§3.7 — human_review attributes, sorted by confidence ascending."""
    stmt = (
        select(Attribute, Product.sku)
        .join(Product, Attribute.product_id == Product.id)
        .where(Attribute.policy_decision == PolicyDecision.human_review)
        .order_by(Attribute.classification_confidence.asc())
    )
    result = await session.execute(stmt)
    return [(row[0], row[1]) for row in result.all()]


async def apply_review_decision(
    session: AsyncSession,
    attribute_id: uuid.UUID,
    *,
    action: str,
    edited_value: str | None = None,
    reviewer_note: str | None = None,
) -> AttributeDetailRead:
    """§3.8 — apply approve/reject/edit and return updated attribute detail."""
    attribute = await session.get(Attribute, attribute_id)
    if attribute is None:
        raise NotFoundError(f"Attribute {attribute_id} not found")

    detail: dict = {"action": action}
    if reviewer_note:
        detail["reviewer_note"] = reviewer_note

    if action == "approve":
        attribute.policy_decision = PolicyDecision.publish
        attribute.classification = Classification.verified
    elif action == "reject":
        attribute.policy_decision = PolicyDecision.blocked
    elif action == "edit":
        if edited_value is not None:
            attribute.attr_value = edited_value
            detail["edited_value"] = edited_value
        attribute.policy_decision = PolicyDecision.publish
        attribute.classification = Classification.verified

    session.add(
        AuditLog(
            attribute_id=attribute.id,
            document_id=attribute.source_document_id,
            event_type=AuditEventType.human_reviewed,
            detail=detail,
        )
    )
    await session.commit()
    await session.refresh(attribute)

    # Return the full detail response per §3.8
    return await attribute_service.get_attribute_detail(session, attribute_id)
