"""LangGraph pipeline state — the single object threaded through every node.

Logging a summary of this object at each node transition is what makes the
pipeline inspectable end-to-end and backs the audit trail.
"""
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

CrossDocResult = Literal["agrees", "contradicts", "no_corroboration"]
PolicyOutcome = Literal["publish", "human_review", "blocked"]
ClassificationLabel = Literal[
    "verified", "derived", "inferred", "conflicting", "unsupported"
]


class ExtractedClaim(BaseModel):
    attr_key: str
    attr_value: str
    raw_value: str
    unit: str | None = None
    source_span: str
    extraction_confidence: float = Field(ge=0, le=1)
    # Assigned in write_to_graph so Postgres and Neo4j share one id.
    claim_id: UUID | None = None


class RedTeamFinding(BaseModel):
    check: Literal["unit_consistency", "contradiction", "evidence_sufficiency"]
    result: Literal["pass", "pass_after_normalization", "fail"]
    detail: str


class ClassificationResult(BaseModel):
    classification: ClassificationLabel
    confidence: float = Field(ge=0, le=1)
    reasoning: str


class PipelineState(BaseModel):
    document_id: UUID
    product_id: UUID
    product_sku: str
    doc_type: str
    raw_claims: list[ExtractedClaim] = Field(default_factory=list)
    normalized_claims: list[ExtractedClaim] = Field(default_factory=list)
    cross_doc_results: dict[str, CrossDocResult] = Field(default_factory=dict)
    red_team_findings: dict[str, list[RedTeamFinding]] = Field(default_factory=dict)
    classifications: dict[str, ClassificationResult] = Field(default_factory=dict)
    policy_decisions: dict[str, PolicyOutcome] = Field(default_factory=dict)
    status: str = "queued"
    error: str | None = None
