import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, ForeignKey, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.product import Product


class Classification(str, enum.Enum):
    verified = "verified"
    derived = "derived"
    inferred = "inferred"
    conflicting = "conflicting"
    unsupported = "unsupported"


class PolicyDecision(str, enum.Enum):
    publish = "publish"
    human_review = "human_review"
    blocked = "blocked"


class Attribute(Base):
    __tablename__ = "attributes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), index=True)
    attr_key: Mapped[str] = mapped_column(index=True)
    attr_value: Mapped[str] = mapped_column(Text)
    raw_value: Mapped[str | None] = mapped_column(Text)
    unit: Mapped[str | None]
    source_document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id"))
    source_span: Mapped[str | None] = mapped_column(Text)
    extraction_confidence: Mapped[float | None] = mapped_column(Float)
    classification: Mapped[Classification | None] = mapped_column(
        SAEnum(Classification, name="classification_enum")
    )
    classification_confidence: Mapped[float | None] = mapped_column(Float)
    reasoning: Mapped[str | None] = mapped_column(Text)
    policy_decision: Mapped[PolicyDecision | None] = mapped_column(
        SAEnum(PolicyDecision, name="policy_decision_enum"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    product: Mapped["Product"] = relationship(back_populates="attributes")

    __table_args__ = (
        Index("ix_attributes_product_attr_key", "product_id", "attr_key"),
    )
