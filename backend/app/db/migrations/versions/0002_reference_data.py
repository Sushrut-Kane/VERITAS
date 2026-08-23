"""reference data tables

Revision ID: 0002_reference_data
Revises: 0001_initial
Create Date: 2026-08-23
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "0002_reference_data"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "manufacturers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("manufacturer_name", sa.String(), nullable=False),
        sa.Column("manufacturer_code", sa.String(), server_default="", nullable=False),
        sa.Column("brand_name", sa.String(), server_default="", nullable=False),
        sa.Column("brand_code", sa.String(), server_default="", nullable=False),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_manufacturers_name", "manufacturers", ["manufacturer_name"])
    op.create_index("ix_manufacturers_code", "manufacturers", ["manufacturer_code"])

    op.create_table(
        "lov_attributes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("classpath", sa.String(), nullable=False),
        sa.Column("leaf_node", sa.String(), server_default="", nullable=False),
        sa.Column("filtering", sa.String(), server_default="", nullable=False),
        sa.Column("attribute_label", sa.String(), nullable=False),
        sa.Column(
            "attribute_values",
            postgresql.ARRAY(sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("normalized_label", sa.String(), server_default="", nullable=False),
        sa.Column(
            "normalized_values",
            postgresql.ARRAY(sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("guidelines", sa.Text(), server_default="", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lov_attributes_classpath", "lov_attributes", ["classpath"])
    op.create_index("ix_lov_attributes_label", "lov_attributes", ["attribute_label"])

    op.create_table(
        "uom_abbreviations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("measurement_type", sa.String(), nullable=False),
        sa.Column("approved_abbreviation", sa.String(), nullable=False),
        sa.Column(
            "accepted_variants",
            postgresql.ARRAY(sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("example", sa.String(), server_default="", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "fraction_decimal",
        sa.Column("fraction", sa.String(), nullable=False),
        sa.Column("decimal_value", sa.Numeric(), nullable=False),
        sa.PrimaryKeyConstraint("fraction"),
    )


def downgrade() -> None:
    op.drop_table("fraction_decimal")
    op.drop_table("uom_abbreviations")
    op.drop_table("lov_attributes")
    op.drop_table("manufacturers")
