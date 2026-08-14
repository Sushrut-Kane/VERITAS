"""Wraps the compiled LangGraph pipeline for FastAPI BackgroundTasks.

Ensures a pipeline crash never leaves a document silently stuck in "queued":
status transitions queued -> processing -> done|error, and a pipeline_error
audit row is written on any unhandled exception.
"""
from uuid import UUID

from app.agents.graph_pipeline import pipeline
from app.core.logging import get_logger
from app.db.models.audit_log import AuditEventType, AuditLog
from app.db.models.document import Document, DocumentStatus
from app.db.models.product import Product
from app.db.session import AsyncSessionLocal
from app.schemas.pipeline_state import PipelineState

logger = get_logger(__name__)


async def _set_status(
    document_id: UUID, status: DocumentStatus, error: str | None = None
) -> None:
    async with AsyncSessionLocal() as session:
        document = await session.get(Document, document_id)
        if document is None:
            return
        document.status = status
        if error is not None:
            document.error = error
        await session.commit()


async def _build_initial_state(document_id: UUID) -> PipelineState | None:
    async with AsyncSessionLocal() as session:
        document = await session.get(Document, document_id)
        if document is None:
            return None
        product = await session.get(Product, document.product_id)
        if product is None:
            return None
        return PipelineState(
            document_id=document.id,
            product_id=document.product_id,
            product_sku=product.sku,
            doc_type=document.doc_type.value,
        )


async def run_pipeline(document_id: UUID) -> dict | None:
    initial = await _build_initial_state(document_id)
    if initial is None:
        logger.error("pipeline_document_missing", document_id=str(document_id))
        return None

    await _set_status(document_id, DocumentStatus.processing)
    try:
        result = await pipeline.ainvoke(initial.model_dump())
        await _set_status(document_id, DocumentStatus.done)
        logger.info("pipeline_complete", document_id=str(document_id))
        return dict(result)
    except Exception as exc:  # never leave the document stuck in processing
        logger.exception("pipeline_failed", document_id=str(document_id))
        await _set_status(document_id, DocumentStatus.error, error=str(exc))
        async with AsyncSessionLocal() as session:
            session.add(
                AuditLog(
                    document_id=document_id,
                    event_type=AuditEventType.pipeline_error,
                    detail={"error": str(exc)},
                )
            )
            await session.commit()
        return None
