"""Pydantic schemas for document and pipeline-status endpoints (§3.2, §3.3)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.db.models.document import DocType, DocumentStatus


class DocumentUploadResponse(BaseModel):
    """§3.2 response — pipeline started async."""

    document_id: UUID
    status: str = "queued"


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    filename: str
    doc_type: DocType
    storage_path: str
    status: DocumentStatus
    error: str | None = None
    uploaded_at: datetime


class PipelineStatusRead(BaseModel):
    """§3.3 response — polled by frontend every ~1.5s."""

    document_id: UUID
    status: str  # "extracting | cross_checking | red_teaming | classifying | policy_deciding | done | error"
    attributes_processed: int = 0
    attributes_total: int = 0
    error: str | None = None
