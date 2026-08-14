import uuid

from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import SessionDep
from app.db.models.attribute import Attribute
from app.db.models.audit_log import AuditLog
from app.schemas.document import AuditEntry, PipelineStatusRead
from app.services import document_service

router = APIRouter(tags=["pipeline"])


@router.get("/pipeline-status/{document_id}", response_model=PipelineStatusRead)
async def pipeline_status(document_id: uuid.UUID, session: SessionDep):
    document = await document_service.get_document(session, document_id)

    attr_rows = await session.execute(
        select(Attribute).where(Attribute.source_document_id == document_id)
    )
    attributes = list(attr_rows.scalars().all())

    by_decision: dict[str, int] = {}
    for attribute in attributes:
        if attribute.policy_decision is not None:
            key = attribute.policy_decision.value
            by_decision[key] = by_decision.get(key, 0) + 1

    audit_rows = await session.execute(
        select(AuditLog)
        .where(AuditLog.document_id == document_id)
        .order_by(AuditLog.created_at)
    )
    audit_log = [AuditEntry.model_validate(row) for row in audit_rows.scalars().all()]

    return PipelineStatusRead(
        document_id=document.id,
        status=document.status,
        error=document.error,
        attributes_total=len(attributes),
        attributes_by_decision=by_decision,
        audit_log=audit_log,
    )
