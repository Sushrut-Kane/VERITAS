import uuid

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.schemas.attribute import AttributeRead
from app.schemas.review import (
    ReviewDecisionRequest,
    ReviewDecisionResponse,
    ReviewQueueItem,
)
from app.services import review_service

router = APIRouter(prefix="/review", tags=["review"])


@router.get("/queue", response_model=list[ReviewQueueItem])
async def review_queue(session: SessionDep, _: CurrentUser):
    rows = await review_service.list_review_queue(session)
    items: list[ReviewQueueItem] = []
    for attribute, sku in rows:
        base = AttributeRead.model_validate(attribute).model_dump()
        items.append(ReviewQueueItem(**base, product_sku=sku))
    return items


@router.post("/{attribute_id}/decision", response_model=ReviewDecisionResponse)
async def submit_decision(
    attribute_id: uuid.UUID,
    payload: ReviewDecisionRequest,
    session: SessionDep,
    _: CurrentUser,
):
    attribute = await review_service.apply_review_decision(
        session, attribute_id, payload.decision, payload.note
    )
    return ReviewDecisionResponse(
        attribute_id=attribute.id, policy_decision=attribute.policy_decision
    )
