from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from app.db.models.attribute import PolicyDecision
from app.schemas.attribute import AttributeRead


class ReviewQueueItem(AttributeRead):
    product_sku: str | None = None


class ReviewDecisionRequest(BaseModel):
    # Human reviewer overrides the automated policy decision.
    decision: Literal["publish", "blocked"]
    note: str | None = None


class ReviewDecisionResponse(BaseModel):
    attribute_id: UUID
    policy_decision: PolicyDecision
