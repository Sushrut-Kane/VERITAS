"""Import every model so ``Base.metadata`` and Alembic see them."""
from app.db.models.attribute import Attribute, Classification, PolicyDecision
from app.db.models.audit_log import AuditEventType, AuditLog
from app.db.models.document import DocType, Document, DocumentStatus
from app.db.models.product import Product
from app.db.models.reference import (
    FractionDecimal,
    LovAttribute,
    Manufacturer,
    UomAbbreviation,
)

__all__ = [
    "Product",
    "Document",
    "DocType",
    "DocumentStatus",
    "Attribute",
    "Classification",
    "PolicyDecision",
    "AuditLog",
    "AuditEventType",
    "Manufacturer",
    "LovAttribute",
    "UomAbbreviation",
    "FractionDecimal",
]
