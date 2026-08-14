"""Prompt for the classification node."""
import json

CLASSIFICATION_SYSTEM_PROMPT = """You classify a single product attribute into EXACTLY one label.

Labels:
- "verified": single claim or multiple agreeing claims, all red-team checks pass, direct textual evidence.
- "derived": value computed/converted from evidence (e.g. unit-converted) but not stated verbatim in any source.
- "inferred": evidence implies but does not directly state the value.
- "conflicting": the contradiction check failed and did not resolve via normalization.
- "unsupported": the evidence-sufficiency check failed, or no source span survived extraction.

Respond with ONLY a JSON object:
{"classification": "<one label>", "confidence": 0.0, "reasoning": "<one or two sentences a human reviewer can read>"}
"""


def build_classification_prompt(
    attr_key: str,
    claims: list[dict],
    cross_doc_result: str,
    red_team_findings: list[dict],
) -> str:
    context = {
        "attr_key": attr_key,
        "claims": claims,
        "cross_document_result": cross_doc_result,
        "red_team_findings": red_team_findings,
    }
    return (
        "Classify this attribute using the evidence below and return the JSON object.\n\n"
        + json.dumps(context, indent=2, ensure_ascii=False)
    )
