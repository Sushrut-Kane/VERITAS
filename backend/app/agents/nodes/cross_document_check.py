"""cross_document_check node: compare each new claim against existing claims for
the same attribute in the evidence graph. Contradiction takes precedence.
"""
from app.core.logging import get_logger
from app.graph import queries
from app.schemas.pipeline_state import CrossDocResult, PipelineState

logger = get_logger(__name__)

# Relative tolerance for treating two numeric values as equal.
NUMERIC_REL_TOLERANCE = 0.01
NUMERIC_ABS_TOLERANCE = 0.01


def _to_float(value) -> float | None:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def _values_match(a: str, b: str) -> bool:
    a_num, b_num = _to_float(a), _to_float(b)
    if a_num is not None and b_num is not None:
        tolerance = max(NUMERIC_ABS_TOLERANCE, abs(a_num) * NUMERIC_REL_TOLERANCE)
        return abs(a_num - b_num) <= tolerance
    return str(a).strip().lower() == str(b).strip().lower()


async def cross_document_check(state: PipelineState) -> dict:
    results: dict[str, CrossDocResult] = dict(state.cross_doc_results)

    for claim in state.normalized_claims:
        existing = await queries.find_existing_claims_for_attribute(
            state.product_sku, claim.attr_key, exclude_claim_id=claim.claim_id
        )
        if not existing:
            results[claim.attr_key] = "no_corroboration"
            continue

        verdict: CrossDocResult = "no_corroboration"
        for other in existing:
            if _values_match(claim.attr_value, other["value"]):
                if claim.claim_id is not None:
                    await queries.link_claims_agree(claim.claim_id, other["claim_id"])
                if verdict != "contradicts":
                    verdict = "agrees"
            else:
                if claim.claim_id is not None:
                    await queries.link_claims_contradict(
                        claim.claim_id, other["claim_id"]
                    )
                verdict = "contradicts"
        results[claim.attr_key] = verdict

    logger.info("cross_document_check_done", results=results)
    return {"cross_doc_results": results, "status": "cross_checked"}
