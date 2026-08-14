import uuid

from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile, status

from app.api.deps import CurrentUser, SessionDep
from app.db.models.document import DocType
from app.schemas.document import DocumentRead
from app.services import document_service, product_service
from app.worker.pipeline_runner import run_pipeline

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    session: SessionDep,
    background_tasks: BackgroundTasks,
    _: CurrentUser,
    product_sku: str = Form(...),
    doc_type: DocType = Form(...),
    file: UploadFile = File(...),
    product_name: str | None = Form(None),
):
    product = await product_service.get_or_create_product(
        session, product_sku, product_name
    )
    document = await document_service.create_document(
        session,
        product_id=product.id,
        filename=file.filename or "upload.bin",
        doc_type=doc_type,
        file=file,
    )
    # Hackathon scale: BackgroundTasks is enough (no Celery/Redis needed).
    background_tasks.add_task(run_pipeline, document.id)
    return document


@router.get("", response_model=list[DocumentRead])
async def list_documents(session: SessionDep, product_id: uuid.UUID | None = None):
    return await document_service.list_documents(session, product_id)


@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(document_id: uuid.UUID, session: SessionDep):
    return await document_service.get_document(session, document_id)
