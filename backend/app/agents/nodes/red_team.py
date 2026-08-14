"""red_team_attack node: three adversarial checks, at most one LLM call.

1. unit_consistency  — deterministic (did normalization succeed for all claims?)
2. contradiction     — deterministic (reads cross_doc_results; resolves the
                       unit-only mismatch case to pass_after_normalization)
3. evidence_sufficiency — one LLM call (offline heuristic when no API key)
"""
from collections import defaultdict

from app.agents import llm
from app.agents.nodes.normalize_units import CANONICAL_UNITS
from app.agents.prompts.evidence_sufficiency_prompt import (
    EVIDENCE_SUFFICIENCY_SYSTEM_PROMPT,
    build_evidence_prompt,
)
from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.pipeline_state import ExtractedClaim, PipelineState, RedTeamFinding

logger = get_logger(__name__)


def _unit_consistency_check(
    attr_key: str, claims: list[ExtractedClaim]
) -> RedTeamFinding:
    target = CANONICAL_UNITS.get(attr_key)
    if target is None:
        return RedTeamFinding(
            check="unit_consistency",
            result="pass",
            detail="No canonical unit defined for this attribute; no check required.",
        )
    if all((claim.unit or "") == target for claim in claims):
        return RedTeamFinding(
            check="unit_consistency",
            result="pass",
            detail=f"All claims normalized to canonical unit '{target}'.",
        )
    seen = sorted({(claim.unit or "∅") for claim in claims})
    return RedTeamFinding(
        check="unit_consistency",
        result="fail",
        detail=f"One or more claims did not normalize to '{target}' (units seen: {seen}).",
    )


def _contradiction_check(
    attr_key: str, state: PipelineState, claims: list[ExtractedClaim]
) -> RedTeamFinding:
    verdict = state.cross_doc_results.get(attr_key, "no_corroboration")
    if verdict == "contradicts":
        return RedTeamFinding(
            check="contradiction",
            result="fail",
            detail="Sources disagree on the value even after unit normalization.",
        )
    if verdict == "agrees":
        raw_units = {
            (c.unit or "").strip().lower()
            for c in state.raw_claims
            if c.attr_key == attr_key and c.unit
        }
        if len(raw_units) > 1:
            return RedTeamFinding(
                check="contradiction",
                result="pass_after_normalization",
                detail="Sources used different units but agree after normalization.",
            )
        return RedTeamFinding(
            check="contradiction", result="pass", detail="Sources agree."
        )
    return RedTeamFinding(
        check="contradiction",
        result="pass",
        detail="No corroborating source; nothing to contradict.",
    )


async def _evidence_sufficiency_check(
    claims: list[ExtractedClaim],
) -> RedTeamFinding:
    if not settings.llm_enabled:
        has_span = all(c.source_span and c.source_span.strip() for c in claims)
        return RedTeamFinding(
            check="evidence_sufficiency",
            result="pass" if has_span else "fail",
            detail="Offline heuristic: judged on presence of a source span.",
        )
    payload = [
        {"attr_value": c.attr_value, "source_span": c.source_span} for c in claims
    ]
    try:
        raw = await llm.complete(
            EVIDENCE_SUFFICIENCY_SYSTEM_PROMPT, build_evidence_prompt(payload)
        )
        data = llm.parse_json_block(raw)
        result = data.get("result", "fail")
        result = result if result in ("pass", "fail") else "fail"
        return RedTeamFinding(
            check="evidence_sufficiency",
            result=result,
            detail=str(data.get("detail", "")),
        )
    except Exception as exc:
        logger.warning("evidence_sufficiency_llm_failed", error=str(exc))
        return RedTeamFinding(
            check="evidence_sufficiency",
            result="fail",
            detail="Evidence auditor unavailable; conservatively marked unsupported.",
        )


async def red_team_attack(state: PipelineState) -> dict:
    by_key: dict[str, list[ExtractedClaim]] = defaultdict(list)
    for claim in state.normalized_claims:
        by_key[claim.attr_key].append(claim)

    findings: dict[str, list[RedTeamFinding]] = {}
    for attr_key, claims in by_key.items():
        findings[attr_key] = [
            _unit_consistency_check(attr_key, claims),
            _contradiction_check(attr_key, state, claims),
            await _evidence_sufficiency_check(claims),
        ]

    logger.info(
        "red_team_done",
        flagged=[k for k, fs in findings.items() if any(f.result == "fail" for f in fs)],
    )
    return {"red_team_findings": findings, "status": "red_teamed"}
