"""Prompt for the red-team evidence-sufficiency check."""
import json

EVIDENCE_SUFFICIENCY_SYSTEM_PROMPT = """You are an adversarial evidence auditor.
Given one or more claimed attribute values and the exact source spans they were drawn from,
decide whether the source text DIRECTLY supports the value, or whether it requires inference
beyond what is stated.

Respond with ONLY a JSON object:
{"result": "pass" | "fail", "detail": "<one concise sentence>"}

- "pass": the value is directly and unambiguously supported by the quoted text.
- "fail": the value requires inference, is unsupported, or the span does not actually state it.
"""


def build_evidence_prompt(payload: list[dict]) -> str:
    return (
        "Judge whether the following attribute claims are directly supported by "
        "their source spans. Return a single overall verdict as JSON.\n\n"
        + json.dumps(payload, indent=2, ensure_ascii=False)
    )
