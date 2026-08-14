"""§3.3  GET /pipeline-status/{document_id}
Frontend polls this every ~1.5s while status != "done".
"""
import uuid

from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import SessionDep
from app.db.models.attribute import Attribute
from app.db.models.document import DocumentStatus
from app.schemas.document import PipelineStatusRead
from app.services import document_service

router = APIRouter(tags=["pipeline"])


def _map_status(doc_status: DocumentStatus) -> str:
    """Map internal document status to the contract's status string."""
    if doc_status == DocumentStatus.queued:
        return "extracting"
    if doc_status == DocumentStatus.processing:
        return "extracting"
    if doc_status == DocumentStatus.done:
        return "done"
    return "error"


@router.get("/pipeline-status/{document_id}", response_model=PipelineStatusRead)
async def pipeline_status(document_id: uuid.UUID, session: SessionDep):
    document = await document_service.get_document(session, document_id)

    attr_rows = await session.execute(
        select(Attribute).where(Attribute.source_document_id == document_id)
    )
    attributes = list(attr_rows.scalars().all())

    # Count how many have completed the full pipeline (have a policy_decision)
    processed = sum(1 for a in attributes if a.policy_decision is not None)

    return PipelineStatusRead(
        document_id=document.id,
        status=_map_status(document.status),
        attributes_processed=processed,
        attributes_total=len(attributes),
        error=document.error,
    )
