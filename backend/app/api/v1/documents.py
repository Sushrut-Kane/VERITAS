"""§3.2  POST /products/{product_id}/documents
Documents are now nested under products as the contract specifies.
"""
import uuid

from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile, status

from app.api.deps import CurrentUser, SessionDep
from app.db.models.document import DocType
from app.schemas.document import DocumentRead, DocumentUploadResponse
from app.services import document_service, product_service
from app.worker.pipeline_runner import run_pipeline

router = APIRouter(prefix="/products", tags=["documents"])


@router.post(
    "/{product_id}/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    product_id: uuid.UUID,
    session: SessionDep,
    background_tasks: BackgroundTasks,
    _: CurrentUser,
    doc_type: DocType = Form(...),
    file: UploadFile = File(...),
):
    # Verify product exists (raises 404 if not)
    await product_service.get_product(session, product_id)
    document = await document_service.create_document(
        session,
        product_id=product_id,
        filename=file.filename or "upload.bin",
        doc_type=doc_type,
        file=file,
    )
    # Hackathon scale: BackgroundTasks is enough (no Celery/Redis needed).
    background_tasks.add_task(run_pipeline, document.id)
    return DocumentUploadResponse(document_id=document.id, status="queued")


@router.get("/{product_id}/documents", response_model=list[DocumentRead])
async def list_product_documents(product_id: uuid.UUID, session: SessionDep):
    await product_service.get_product(session, product_id)  # 404 if missing
    return await document_service.list_documents(session, product_id)
