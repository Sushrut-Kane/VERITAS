"""Inch fraction <-> decimal conversion (house style uses mixed fractions)."""
import re
from fractions import Fraction

_MIXED_RE = re.compile(r"^(?:(\d+)[-\s])?(\d+)/(\d+)$")
_WHOLE_RE = re.compile(r"^\d+(?:\.\d+)?$")


def inch_fraction_to_decimal(text: str) -> float | None:
    """``'50-1/4'`` -> ``50.25``; ``'1/2'`` -> ``0.5``; ``'3'`` -> ``3.0``."""
    if text is None:
        return None
    token = text.strip().strip('"').strip()
    if not token:
        return None
    if _WHOLE_RE.match(token):
        return float(token)
    match = _MIXED_RE.match(token)
    if not match:
        return None
    whole = int(match.group(1)) if match.group(1) else 0
    num, den = int(match.group(2)), int(match.group(3))
    if den == 0:
        return None
    return whole + num / den


def decimal_to_inch_fraction(value: float, max_denominator: int = 16) -> str:
    """``50.25`` -> ``'50-1/4'``; ``0.5`` -> ``'1/2'``; ``1.0`` -> ``'1'``."""
    frac = Fraction(value).limit_denominator(max_denominator)
    whole = frac.numerator // frac.denominator
    remainder = frac - whole
    if remainder == 0:
        return str(whole)
    frac_str = f"{remainder.numerator}/{remainder.denominator}"
    return frac_str if whole == 0 else f"{whole}-{frac_str}"
