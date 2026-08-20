"""Unit-of-measure canonicalization + the "space between number and unit" rule."""

# variant (lowercased) -> approved abbreviation
_VARIANTS: dict[str, str] = {
    "inches": "in", "inch": "in", "in.": "in", '"': "in", "in": "in",
    "feet": "ft", "foot": "ft", "ft.": "ft", "ft": "ft",
    "millimeter": "mm", "millimetre": "mm", "mm": "mm",
    "centimeter": "cm", "centimetre": "cm", "cm": "cm",
    "meter": "m", "metre": "m", "m": "m",
    "pound": "lb", "pounds": "lb", "lbs": "lb", "lb": "lb",
    "ounce": "oz", "ounces": "oz", "oz": "oz",
    "gram": "g", "grams": "g", "g": "g",
    "kilogram": "kg", "kilograms": "kg", "kg": "kg",
    "volt": "V", "volts": "V", "v": "V",
    "amp": "A", "amps": "A", "ampere": "A", "amperes": "A", "a": "A",
    "watt": "W", "watts": "W", "w": "W",
    "kilowatt": "kW", "kw": "kW",
    "hertz": "Hz", "hz": "Hz",
    "decibel": "dB", "db": "dB", "dba": "dBA",
    "degree": "deg", "degrees": "deg",
    "piece": "pc", "pieces": "pc", "pcs": "pc", "pc": "pc",
    "each": "ea", "ea": "ea",
    "gallon": "gal", "gallons": "gal", "gal": "gal",
    "liter": "L", "litre": "L", "l": "L",
    "rpm": "RPM",
    "psi": "psi", "bar": "bar",
    "grit": "grit",
}


def canonical_uom(unit: str | None) -> str:
    """Map a raw unit spelling to its approved abbreviation."""
    if not unit:
        return ""
    key = unit.strip().lower().rstrip(".")
    return _VARIANTS.get(key, unit.strip())


def format_quantity(value: str | float, unit: str | None) -> str:
    """``(120, 'volts')`` -> ``'120 V'`` (single space, approved abbreviation)."""
    canonical = canonical_uom(unit)
    text = str(value).strip()
    return f"{text} {canonical}".strip() if canonical else text
