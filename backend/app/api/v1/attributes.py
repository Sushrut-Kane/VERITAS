import uuid

from fastapi import APIRouter

from app.api.deps import SessionDep
from app.schemas.attribute import AttributeGraph, AttributeRead
from app.services import attribute_service

router = APIRouter(prefix="/attributes", tags=["attributes"])


@router.get("/{attribute_id}", response_model=AttributeRead)
async def get_attribute(attribute_id: uuid.UUID, session: SessionDep):
    return await attribute_service.get_attribute(session, attribute_id)


@router.get("/{attribute_id}/graph", response_model=AttributeGraph)
async def get_attribute_graph(attribute_id: uuid.UUID, session: SessionDep):
    return await attribute_service.get_attribute_graph(session, attribute_id)
