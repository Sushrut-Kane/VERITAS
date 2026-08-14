from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.db.models.attribute import Classification, PolicyDecision


class AttributeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    attr_key: str
    attr_value: str
    raw_value: str | None
    unit: str | None
    source_document_id: UUID
    source_span: str | None
    extraction_confidence: float | None
    classification: Classification | None
    classification_confidence: float | None
    reasoning: str | None
    policy_decision: PolicyDecision | None
    created_at: datetime


class GraphNode(BaseModel):
    id: str
    labels: list[str]
    properties: dict


class GraphEdge(BaseModel):
    type: str
    source: str
    target: str


class AttributeGraph(BaseModel):
    attribute_id: UUID
    attr_key: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]
