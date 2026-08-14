import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import NotFoundError
from app.db.models.document import DocType, Document, DocumentStatus


async def create_document(
    session: AsyncSession,
    *,
    product_id: uuid.UUID,
    filename: str,
    doc_type: DocType,
    file: UploadFile,
) -> Document:
    document_id = uuid.uuid4()
    dest_dir = Path(settings.storage_dir) / str(document_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / filename
    dest_path.write_bytes(await file.read())

    document = Document(
        id=document_id,
        product_id=product_id,
        filename=filename,
        doc_type=doc_type,
        storage_path=str(dest_path),
        status=DocumentStatus.queued,
    )
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document


async def get_document(session: AsyncSession, document_id: uuid.UUID) -> Document:
    document = await session.get(Document, document_id)
    if document is None:
        raise NotFoundError(f"Document {document_id} not found")
    return document


async def list_documents(
    session: AsyncSession, product_id: uuid.UUID | None = None
) -> list[Document]:
    stmt = select(Document).order_by(Document.uploaded_at.desc())
    if product_id is not None:
        stmt = stmt.where(Document.product_id == product_id)
    result = await session.execute(stmt)
    return list(result.scalars().all())
