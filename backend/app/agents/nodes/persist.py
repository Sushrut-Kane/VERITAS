"""persist node: write attribute rows + a per-stage audit trail to Postgres."""
import uuid

from app.core.logging import get_logger
from app.db.models.attribute import Attribute, Classification, PolicyDecision
from app.db.models.audit_log import AuditEventType, AuditLog
from app.db.session import AsyncSessionLocal
from app.schemas.pipeline_state import PipelineState

logger = get_logger(__name__)


def _build_stage_audit(state: PipelineState) -> list[tuple[AuditEventType, dict]]:
    """One audit row per pipeline stage that ran — shows the journey."""
    return [
        (
            AuditEventType.extracted,
            {
                "claims": len(state.raw_claims),
                "attr_keys": sorted({c.attr_key for c in state.raw_claims}),
            },
        ),
        (AuditEventType.normalized, {"normalized": len(state.normalized_claims)}),
        (
            AuditEventType.written_to_graph,
            {"claims_written": len(state.normalized_claims)},
        ),
        (AuditEventType.cross_checked, {"results": state.cross_doc_results}),
        (
            AuditEventType.red_team_flagged,
            {
                "findings": {
                    key: [f.model_dump() for f in findings]
                    for key, findings in state.red_team_findings.items()
                }
            },
        ),
        (
            AuditEventType.classified,
            {
                "classifications": {
                    key: result.model_dump()
                    for key, result in state.classifications.items()
                }
            },
        ),
        (AuditEventType.policy_decided, {"decisions": dict(state.policy_decisions)}),
    ]


async def persist(state: PipelineState) -> dict:
    async with AsyncSessionLocal() as session:
        for claim in state.normalized_claims:
            classification = state.classifications.get(claim.attr_key)
            policy = state.policy_decisions.get(claim.attr_key)
            session.add(
                Attribute(
                    id=claim.claim_id or uuid.uuid4(),
                    product_id=state.product_id,
                    attr_key=claim.attr_key,
                    attr_value=claim.attr_value,
                    raw_value=claim.raw_value,
                    unit=claim.unit,
                    source_document_id=state.document_id,
                    source_span=claim.source_span,
                    extraction_confidence=claim.extraction_confidence,
                    classification=(
                        Classification(classification.classification)
                        if classification
                        else None
                    ),
                    classification_confidence=(
                        classification.confidence if classification else None
                    ),
                    reasoning=classification.reasoning if classification else None,
                    policy_decision=PolicyDecision(policy) if policy else None,
                )
            )

        for event_type, detail in _build_stage_audit(state):
            session.add(
                AuditLog(
                    document_id=state.document_id,
                    event_type=event_type,
                    detail=detail,
                )
            )

        await session.commit()

    logger.info("persist_done", attributes=len(state.normalized_claims))
    return {"status": "done"}
