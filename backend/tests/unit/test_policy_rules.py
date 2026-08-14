from app.policy.rules import (
    PUBLISH_CONFIDENCE_THRESHOLD,
    SAFETY_CRITICAL_KEYS,
    decide_policy,
)

import pytest


def test_safety_critical_verified_routes_to_review():
    assert decide_policy("voltage_rating", "verified", 0.99) == "human_review"


def test_safety_critical_derived_routes_to_review():
    assert decide_policy("max_load", "derived", 0.99) == "human_review"


def test_safety_critical_unsupported_is_blocked():
    # 'unsupported' is the one label that bypasses the safety override.
    assert decide_policy("pressure_rating", "unsupported", 0.1) == "blocked"


def test_unsupported_is_blocked():
    assert decide_policy("color", "unsupported", 0.99) == "blocked"


def test_verified_high_confidence_publishes():
    assert decide_policy("color", "verified", PUBLISH_CONFIDENCE_THRESHOLD) == "publish"
    assert decide_policy("color", "verified", 0.99) == "publish"


def test_verified_low_confidence_routes_to_review():
    assert decide_policy("color", "verified", 0.84) == "human_review"


@pytest.mark.parametrize("label", ["derived", "inferred", "conflicting"])
def test_non_verified_labels_route_to_review(label):
    assert decide_policy("color", label, 0.99) == "human_review"


def test_all_safety_keys_present():
    assert SAFETY_CRITICAL_KEYS == {
        "voltage_rating",
        "max_load",
        "max_operating_temp",
        "pressure_rating",
    }


def test_never_publishes_below_threshold_even_when_verified():
    just_below = PUBLISH_CONFIDENCE_THRESHOLD - 0.001
    assert decide_policy("color", "verified", just_below) == "human_review"
