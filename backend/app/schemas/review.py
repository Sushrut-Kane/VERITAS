"""Pydantic schemas for review endpoints (§3.7, §3.8)."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from app.schemas.attribute import AttributeDetailRead


class ReviewQueueItem(BaseModel):
    """Same shape as AttributeRead but with product_sku for context."""

    id: UUID
    attr_key: str
    attr_value: str
    classification: str | None = None
    classification_confidence: float | None = None
    policy_decision: str | None = None
    source_count: int = 1


class ReviewDecisionRequest(BaseModel):
    """§3.8 request body for POST /attributes/{id}/review."""

    action: Literal["approve", "reject", "edit"]
    edited_value: str | None = None
    reviewer_note: str | None = None


class ReviewDecisionResponse(AttributeDetailRead):
    """Response to a review action — full attribute detail plus updated audit_log."""

    pass
