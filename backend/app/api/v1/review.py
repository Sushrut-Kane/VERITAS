"""§3.7  GET /review-queue
Filtered to policy_decision = human_review, sorted by classification_confidence ascending.
"""
from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.schemas.attribute import AttributeRead
from app.services import review_service

router = APIRouter(tags=["review"])


@router.get("/review-queue", response_model=list[AttributeRead])
async def review_queue(session: SessionDep, _: CurrentUser):
    """§3.7 — same shape as attributes list, filtered and sorted."""
    rows = await review_service.list_review_queue(session)
    return [
        AttributeRead(
            id=attr.id,
            attr_key=attr.attr_key,
            attr_value=attr.attr_value,
            classification=attr.classification,
            classification_confidence=attr.classification_confidence,
            policy_decision=attr.policy_decision,
            source_count=1,  # TODO: compute from graph
        )
        for attr, _sku in rows
    ]
