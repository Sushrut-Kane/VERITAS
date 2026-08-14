from app.agents.nodes.normalize_units import CANONICAL_UNITS, _normalize_one
from app.schemas.pipeline_state import ExtractedClaim


def _claim(attr_key: str, raw: str, unit: str | None) -> ExtractedClaim:
    return ExtractedClaim(
        attr_key=attr_key,
        attr_value=raw,
        raw_value=raw,
        unit=unit,
        source_span="span",
        extraction_confidence=0.9,
    )


def test_fahrenheit_to_celsius():
    result = _normalize_one(_claim("max_operating_temp", "176", "°F"))
    assert result.unit == "degC"
    assert abs(float(result.attr_value) - 80.0) < 0.1


def test_celsius_passthrough():
    result = _normalize_one(_claim("max_operating_temp", "80", "°C"))
    assert result.unit == "degC"
    assert abs(float(result.attr_value) - 80.0) < 0.1


def test_inch_to_millimeter():
    result = _normalize_one(_claim("length", "1", "in"))
    assert result.unit == "mm"
    assert abs(float(result.attr_value) - 25.4) < 0.01


def test_voltage_stays_volts():
    result = _normalize_one(_claim("voltage_rating", "230", "V"))
    assert result.unit == "V"
    assert abs(float(result.attr_value) - 230.0) < 0.001


def test_unrecognized_unit_keeps_raw_value():
    result = _normalize_one(_claim("length", "5", "blorp"))
    # Left as raw_value so the red-team unit check flags it later.
    assert result.attr_value == "5"


def test_attribute_without_canonical_unit_is_unchanged():
    result = _normalize_one(_claim("color", "red", None))
    assert result.attr_value == "red"
    assert result.unit is None


def test_canonical_units_cover_safety_keys():
    for key in ("max_operating_temp", "voltage_rating", "pressure_rating", "max_load"):
        assert key in CANONICAL_UNITS
