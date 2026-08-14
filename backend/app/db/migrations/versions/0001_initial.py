"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-14
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("sku", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_products_sku", "products", ["sku"], unique=True)

    op.create_table(
        "documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column(
            "doc_type",
            sa.Enum("pdf_spec", "image", "catalog", "web", name="doc_type_enum"),
            nullable=False,
        ),
        sa.Column("storage_path", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "queued", "processing", "done", "error", name="document_status_enum"
            ),
            server_default="queued",
            nullable=False,
        ),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column(
            "uploaded_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_documents_product_id", "documents", ["product_id"])

    op.create_table(
        "attributes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("attr_key", sa.String(), nullable=False),
        sa.Column("attr_value", sa.Text(), nullable=False),
        sa.Column("raw_value", sa.Text(), nullable=True),
        sa.Column("unit", sa.String(), nullable=True),
        sa.Column("source_document_id", sa.Uuid(), nullable=False),
        sa.Column("source_span", sa.Text(), nullable=True),
        sa.Column("extraction_confidence", sa.Float(), nullable=True),
        sa.Column(
            "classification",
            sa.Enum(
                "verified",
                "derived",
                "inferred",
                "conflicting",
                "unsupported",
                name="classification_enum",
            ),
            nullable=True,
        ),
        sa.Column("classification_confidence", sa.Float(), nullable=True),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column(
            "policy_decision",
            sa.Enum(
                "publish", "human_review", "blocked", name="policy_decision_enum"
            ),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["source_document_id"], ["documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_attributes_product_id", "attributes", ["product_id"])
    op.create_index("ix_attributes_attr_key", "attributes", ["attr_key"])
    op.create_index(
        "ix_attributes_policy_decision", "attributes", ["policy_decision"]
    )
    op.create_index(
        "ix_attributes_product_attr_key", "attributes", ["product_id", "attr_key"]
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=True),
        sa.Column("attribute_id", sa.Uuid(), nullable=True),
        sa.Column(
            "event_type",
            sa.Enum(
                "extracted",
                "normalized",
                "written_to_graph",
                "cross_checked",
                "red_team_flagged",
                "classified",
                "policy_decided",
                "human_reviewed",
                "pipeline_error",
                name="audit_event_type_enum",
            ),
            nullable=False,
        ),
        sa.Column(
            "detail",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["attribute_id"], ["attributes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_document_id", "audit_logs", ["document_id"])
    op.create_index("ix_audit_logs_attribute_id", "audit_logs", ["attribute_id"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("attributes")
    op.drop_table("documents")
    op.drop_table("products")
    for enum_name in (
        "audit_event_type_enum",
        "policy_decision_enum",
        "classification_enum",
        "document_status_enum",
        "doc_type_enum",
    ):
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
