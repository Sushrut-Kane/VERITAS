"""Explicit, readable policy rule table.

Deliberately not data-driven — it must be readable at a glance during demo Q&A.
Every branch is unit-tested in tests/unit/test_policy_rules.py.
"""

SAFETY_CRITICAL_KEYS = {
    "voltage_rating",
    "max_load",
    "max_operating_temp",
    "pressure_rating",
}

PUBLISH_CONFIDENCE_THRESHOLD = 0.85


def decide_policy(attr_key: str, classification: str, confidence: float) -> str:
    """Return one of: 'publish', 'human_review', 'blocked'."""
    if attr_key in SAFETY_CRITICAL_KEYS and classification != "unsupported":
        return "human_review"
    if classification == "unsupported":
        return "blocked"
    if classification == "verified" and confidence >= PUBLISH_CONFIDENCE_THRESHOLD:
        return "publish"
    if classification == "verified":
        return "human_review"
    if classification in ("derived", "inferred", "conflicting"):
        return "human_review"
    return "human_review"  # safe default, never falls through to publish
