import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.attribute import Attribute
    from app.db.models.document import Document


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    sku: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    name: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    documents: Mapped[list["Document"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    attributes: Mapped[list["Attribute"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
