"""normalize_units node: deterministic, pint-based unit normalization.

On parse failure the value is left as raw_value and flagged implicitly — the
red-team unit_consistency check surfaces it later, which is the correct behavior.
"""
from app.core.logging import get_logger
from app.schemas.pipeline_state import ExtractedClaim, PipelineState

logger = get_logger(__name__)

# Canonical unit per attribute key. Extend as new attributes appear.
CANONICAL_UNITS: dict[str, str] = {
    "max_operating_temp": "degC",
    "min_operating_temp": "degC",
    "operating_temp": "degC",
    "voltage": "V",
    "voltage_rating": "V",
    "current": "A",
    "power": "W",
    "weight": "kg",
    "max_load": "kg",
    "length": "mm",
    "width": "mm",
    "height": "mm",
    "depth": "mm",
    "diameter": "mm",
    "pressure_rating": "bar",
    "frequency": "Hz",
}

# Map common unit spellings to pint-recognized tokens.
_UNIT_ALIASES: dict[str, str] = {
    "°c": "degC", "c": "degC", "celsius": "degC", "degc": "degC",
    "°f": "degF", "f": "degF", "fahrenheit": "degF", "degf": "degF",
    "k": "kelvin", "kelvin": "kelvin",
    "in": "inch", "inch": "inch", "inches": "inch", '"': "inch",
    "mm": "mm", "millimeter": "mm", "millimetre": "mm",
    "cm": "cm", "m": "m", "meter": "m", "metre": "m",
    "v": "V", "volt": "V", "volts": "V",
    "a": "A", "amp": "A", "amps": "A", "ampere": "A",
    "w": "W", "watt": "W", "watts": "W", "kw": "kW",
    "kg": "kg", "g": "g", "lb": "pound", "lbs": "pound", "pound": "pound",
    "bar": "bar", "psi": "psi", "pa": "Pa", "kpa": "kPa",
    "hz": "Hz", "khz": "kHz", "mhz": "MHz",
}

_ureg = None


def _registry():
    global _ureg
    if _ureg is None:
        import pint

        _ureg = pint.UnitRegistry()
    return _ureg


def _canonical_unit_token(unit: str) -> str:
    return _UNIT_ALIASES.get(unit.strip().lower(), unit.strip())


def _normalize_one(claim: ExtractedClaim) -> ExtractedClaim:
    target = CANONICAL_UNITS.get(claim.attr_key)
    if target is None or not claim.unit:
        return claim
    try:
        registry = _registry()
        magnitude = float(str(claim.raw_value).strip())
        source_token = _canonical_unit_token(claim.unit)
        converted = registry.Quantity(magnitude, source_token).to(target)
        return claim.model_copy(
            update={"attr_value": f"{converted.magnitude:g}", "unit": target}
        )
    except Exception as exc:  # unrecognized unit / non-numeric value
        logger.warning(
            "unit_normalization_failed",
            attr_key=claim.attr_key,
            raw_value=claim.raw_value,
            unit=claim.unit,
            error=str(exc),
        )
        return claim.model_copy(update={"attr_value": str(claim.raw_value)})


async def normalize_units(state: PipelineState) -> dict:
    normalized = [_normalize_one(claim) for claim in state.raw_claims]
    logger.info("normalize_units_done", count=len(normalized))
    return {"normalized_claims": normalized, "status": "normalized"}
