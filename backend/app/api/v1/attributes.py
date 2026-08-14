"""§3.5  GET /attributes/{id}
§3.6  GET /attributes/{id}/graph
§3.8  POST /attributes/{id}/review
"""
import uuid

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.schemas.attribute import AttributeDetailRead, AttributeGraph
from app.schemas.review import ReviewDecisionRequest, ReviewDecisionResponse
from app.services import attribute_service, review_service

router = APIRouter(prefix="/attributes", tags=["attributes"])


@router.get("/{attribute_id}", response_model=AttributeDetailRead)
async def get_attribute(attribute_id: uuid.UUID, session: SessionDep):
    """§3.5 — richest response in the system: claims, red-team, audit log."""
    return await attribute_service.get_attribute_detail(session, attribute_id)


@router.get("/{attribute_id}/graph", response_model=AttributeGraph)
async def get_attribute_graph(attribute_id: uuid.UUID, session: SessionDep):
    """§3.6 — small node/edge payload for graph visualization."""
    return await attribute_service.get_attribute_graph(session, attribute_id)


@router.post("/{attribute_id}/review", response_model=ReviewDecisionResponse)
async def submit_review(
    attribute_id: uuid.UUID,
    payload: ReviewDecisionRequest,
    session: SessionDep,
    _: CurrentUser,
):
    """§3.8 — human reviewer approves, rejects, or edits an attribute."""
    return await review_service.apply_review_decision(
        session,
        attribute_id,
        action=payload.action,
        edited_value=payload.edited_value,
        reviewer_note=payload.reviewer_note,
    )
