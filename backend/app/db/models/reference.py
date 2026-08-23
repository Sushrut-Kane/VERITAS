"""Reference-data tables (manufacturers, LOV, UOM, fractions).

Separate from the core pipeline models — populated via ``scripts/load_reference_data.py``.
"""
import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import Numeric, String, Text, Uuid
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Manufacturer(Base):
    __tablename__ = "manufacturers"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    manufacturer_name: Mapped[str] = mapped_column(String(), nullable=False, index=True)
    manufacturer_code: Mapped[str] = mapped_column(String(), default="", index=True)
    brand_name: Mapped[str] = mapped_column(String(), default="")
    brand_code: Mapped[str] = mapped_column(String(), default="")
    embedding = mapped_column(Vector(1536), nullable=True)


class LovAttribute(Base):
    __tablename__ = "lov_attributes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    classpath: Mapped[str] = mapped_column(String(), nullable=False, index=True)
    leaf_node: Mapped[str] = mapped_column(String(), default="")
    filtering: Mapped[str] = mapped_column(String(), default="")
    attribute_label: Mapped[str] = mapped_column(String(), nullable=False, index=True)
    attribute_values: Mapped[list[str]] = mapped_column(
        ARRAY(Text), server_default="{}", nullable=False
    )
    normalized_label: Mapped[str] = mapped_column(String(), default="")
    normalized_values: Mapped[list[str]] = mapped_column(
        ARRAY(Text), server_default="{}", nullable=False
    )
    guidelines: Mapped[str] = mapped_column(Text(), default="")


class UomAbbreviation(Base):
    __tablename__ = "uom_abbreviations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    measurement_type: Mapped[str] = mapped_column(String(), nullable=False)
    approved_abbreviation: Mapped[str] = mapped_column(String(), nullable=False)
    accepted_variants: Mapped[list[str]] = mapped_column(
        ARRAY(Text), server_default="{}", nullable=False
    )
    example: Mapped[str] = mapped_column(String(), default="")


class FractionDecimal(Base):
    __tablename__ = "fraction_decimal"

    fraction: Mapped[str] = mapped_column(String(), primary_key=True)
    decimal_value: Mapped[float] = mapped_column(Numeric(), nullable=False)
