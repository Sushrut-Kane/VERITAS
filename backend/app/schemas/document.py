from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.audit_log import AuditEventType
from app.db.models.document import DocType, DocumentStatus


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    filename: str
    doc_type: DocType
    storage_path: str
    status: DocumentStatus
    error: str | None
    uploaded_at: datetime


class AuditEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_type: AuditEventType
    attribute_id: UUID | None = None
    detail: dict
    created_at: datetime


class PipelineStatusRead(BaseModel):
    document_id: UUID
    status: DocumentStatus
    error: str | None = None
    attributes_total: int = 0
    attributes_by_decision: dict[str, int] = Field(default_factory=dict)
    audit_log: list[AuditEntry] = Field(default_factory=list)
