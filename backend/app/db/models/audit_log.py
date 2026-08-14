import enum
import uuid
from datetime import datetime

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import JSONType


class AuditEventType(str, enum.Enum):
    extracted = "extracted"
    normalized = "normalized"
    written_to_graph = "written_to_graph"
    cross_checked = "cross_checked"
    red_team_flagged = "red_team_flagged"
    classified = "classified"
    policy_decided = "policy_decided"
    human_reviewed = "human_reviewed"
    pipeline_error = "pipeline_error"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("documents.id"), index=True
    )
    attribute_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("attributes.id"), index=True
    )
    event_type: Mapped[AuditEventType] = mapped_column(
        SAEnum(AuditEventType, name="audit_event_type_enum")
    )
    detail: Mapped[dict] = mapped_column(JSONType, default=dict)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
