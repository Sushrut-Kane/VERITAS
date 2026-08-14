from uuid import uuid4

from app.agents.nodes.red_team import _contradiction_check, _unit_consistency_check
from app.schemas.pipeline_state import ExtractedClaim, PipelineState


def _claim(attr_key: str, value: str, unit: str | None) -> ExtractedClaim:
    return ExtractedClaim(
        attr_key=attr_key,
        attr_value=value,
        raw_value=value,
        unit=unit,
        source_span="span",
        extraction_confidence=0.9,
    )


def _state(**overrides) -> PipelineState:
    base = dict(
        document_id=uuid4(),
        product_id=uuid4(),
        product_sku="SKU-1",
        doc_type="pdf_spec",
    )
    base.update(overrides)
    return PipelineState(**base)


def test_unit_consistency_pass_when_normalized():
    finding = _unit_consistency_check(
        "max_operating_temp", [_claim("max_operating_temp", "80", "degC")]
    )
    assert finding.result == "pass"


def test_unit_consistency_fail_when_not_normalized():
    finding = _unit_consistency_check(
        "max_operating_temp", [_claim("max_operating_temp", "80", "blorp")]
    )
    assert finding.result == "fail"


def test_unit_consistency_pass_when_no_canonical_unit():
    finding = _unit_consistency_check("color", [_claim("color", "red", None)])
    assert finding.result == "pass"


def test_contradiction_fail_when_cross_doc_contradicts():
    state = _state(cross_doc_results={"weight": "contradicts"})
    finding = _contradiction_check("weight", state, [_claim("weight", "10", "kg")])
    assert finding.result == "fail"


def test_contradiction_pass_after_normalization_for_unit_only_mismatch():
    raw = [
        _claim("max_operating_temp", "80", "°C"),
        _claim("max_operating_temp", "176", "°F"),
    ]
    state = _state(cross_doc_results={"max_operating_temp": "agrees"}, raw_claims=raw)
    finding = _contradiction_check("max_operating_temp", state, raw)
    assert finding.result == "pass_after_normalization"


def test_contradiction_plain_pass_when_same_unit_agreement():
    raw = [_claim("weight", "10", "kg"), _claim("weight", "10", "kg")]
    state = _state(cross_doc_results={"weight": "agrees"}, raw_claims=raw)
    finding = _contradiction_check("weight", state, raw)
    assert finding.result == "pass"


def test_contradiction_pass_when_no_corroboration():
    state = _state(cross_doc_results={"weight": "no_corroboration"})
    finding = _contradiction_check("weight", state, [_claim("weight", "10", "kg")])
    assert finding.result == "pass"
