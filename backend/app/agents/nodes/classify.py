"""classify node: one classification per attribute (not per claim).

Uses Claude when configured; otherwise falls back to a deterministic rule that
mirrors the classification guidance so the pipeline runs fully offline.
"""
from collections import defaultdict

from app.agents import llm
from app.agents.prompts.classification_prompt import (
    CLASSIFICATION_SYSTEM_PROMPT,
    build_classification_prompt,
)
from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.pipeline_state import (
    ClassificationResult,
    ExtractedClaim,
    PipelineState,
    RedTeamFinding,
)

logger = get_logger(__name__)


def _findings_by_check(findings: list[RedTeamFinding]) -> dict[str, RedTeamFinding]:
    return {finding.check: finding for finding in findings}


def _deterministic_classification(
    claims: list[ExtractedClaim],
    cross_doc: str,
    findings: list[RedTeamFinding],
) -> ClassificationResult:
    checks = _findings_by_check(findings)
    evidence = checks.get("evidence_sufficiency")
    contradiction = checks.get("contradiction")
    unit = checks.get("unit_consistency")

    if evidence is not None and evidence.result == "fail":
        return ClassificationResult(
            classification="unsupported",
            confidence=0.9,
            reasoning="Source text does not directly support the value.",
        )
    if contradiction is not None and contradiction.result == "fail":
        return ClassificationResult(
            classification="conflicting",
            confidence=0.8,
            reasoning="Sources disagree on the value even after normalization.",
        )
    if contradiction is not None and contradiction.result == "pass_after_normalization":
        return ClassificationResult(
            classification="derived",
            confidence=0.85,
            reasoning="Value agrees across sources after unit conversion, not stated verbatim.",
        )
    if unit is not None and unit.result == "fail":
        return ClassificationResult(
            classification="inferred",
            confidence=0.6,
            reasoning="Unit could not be normalized; value inferred from ambiguous evidence.",
        )
    confidences = [c.extraction_confidence for c in claims] or [0.5]
    avg = sum(confidences) / len(confidences)
    return ClassificationResult(
        classification="verified",
        confidence=min(0.99, max(0.5, avg)),
        reasoning="Direct textual evidence with consistent (or single-source) corroboration.",
    )


async def _classify_attribute(
    attr_key: str,
    claims: list[ExtractedClaim],
    cross_doc: str,
    findings: list[RedTeamFinding],
) -> ClassificationResult:
    if not settings.llm_enabled:
        return _deterministic_classification(claims, cross_doc, findings)
    try:
        prompt = build_classification_prompt(
            attr_key,
            [c.model_dump(mode="json") for c in claims],
            cross_doc,
            [f.model_dump() for f in findings],
        )
        raw = await llm.complete(CLASSIFICATION_SYSTEM_PROMPT, prompt)
        return ClassificationResult.model_validate(llm.parse_json_block(raw))
    except Exception as exc:
        logger.warning("classification_llm_failed", attr_key=attr_key, error=str(exc))
        return _deterministic_classification(claims, cross_doc, findings)


async def classify(state: PipelineState) -> dict:
    by_key: dict[str, list[ExtractedClaim]] = defaultdict(list)
    for claim in state.normalized_claims:
        by_key[claim.attr_key].append(claim)

    classifications: dict[str, ClassificationResult] = {}
    for attr_key, claims in by_key.items():
        classifications[attr_key] = await _classify_attribute(
            attr_key,
            claims,
            state.cross_doc_results.get(attr_key, "no_corroboration"),
            state.red_team_findings.get(attr_key, []),
        )

    logger.info(
        "classify_done",
        labels={k: v.classification for k, v in classifications.items()},
    )
    return {"classifications": classifications, "status": "classified"}
