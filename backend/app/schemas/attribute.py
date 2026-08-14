"""Pydantic schemas for attribute endpoints (§3.4, §3.5, §3.6)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.db.models.attribute import Classification, PolicyDecision


# ── §3.4  GET /products/{product_id}/attributes ──────────────────────

class AttributeRead(BaseModel):
    """Summary row used in product-attribute listings and the review queue."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    attr_key: str
    attr_value: str
    classification: Classification | None = None
    classification_confidence: float | None = None
    policy_decision: PolicyDecision | None = None
    source_count: int = 1


class ProductAttributesResponse(BaseModel):
    product_id: UUID
    attributes: list[AttributeRead]


# ── §3.5  GET /attributes/{id} (detail) ─────────────────────────────

class SourceDocumentRef(BaseModel):
    id: UUID
    filename: str
    doc_type: str


class ClaimRead(BaseModel):
    claim_id: UUID
    raw_value: str
    normalized_value: str
    source_document: SourceDocumentRef
    source_span: str
    extraction_confidence: float


class RedTeamFindingRead(BaseModel):
    check: str
    result: str
    detail: str


class AuditLogEntry(BaseModel):
    event_type: str
    created_at: datetime


class AttributeDetailRead(BaseModel):
    """Rich detail response — the heaviest payload in the system."""

    id: UUID
    attr_key: str
    attr_value: str
    classification: Classification | None = None
    classification_confidence: float | None = None
    reasoning: str | None = None
    policy_decision: PolicyDecision | None = None
    claims: list[ClaimRead] = []
    red_team_findings: list[RedTeamFindingRead] = []
    audit_log: list[AuditLogEntry] = []


# ── §3.6  GET /attributes/{id}/graph ─────────────────────────────────

class GraphNode(BaseModel):
    id: str
    type: str
    label: str


class GraphEdge(BaseModel):
    source: str  # "from" in the contract, renamed for Python keyword clash
    target: str  # "to" in the contract
    type: str

    def model_dump(self, **kw):
        """Serialize with 'from'/'to' keys as the contract requires."""
        d = super().model_dump(**kw)
        d["from"] = d.pop("source")
        d["to"] = d.pop("target")
        return d


class AttributeGraph(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
