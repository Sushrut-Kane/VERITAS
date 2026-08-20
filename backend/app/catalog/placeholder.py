"""Placeholder brand filtering.

The Solution Guide flags this as an explicit correctness requirement, so it is a
named, unit-tested function rather than an inline check.
"""

PLACEHOLDER_VALUES = {
    "-- unbranded --",
    "-- no unilog brand --",
    "-- no dib brand --",
    "-- no brand --",
    "-- none --",
}


def is_placeholder(value: str | None) -> bool:
    if value is None:
        return True
    stripped = value.strip()
    if not stripped:
        return True
    lowered = stripped.lower()
    if lowered in PLACEHOLDER_VALUES:
        return True
    # Generic "-- ... --" sentinel form.
    return lowered.startswith("-- ") and lowered.endswith(" --")


def clean_brand(value: str | None) -> str:
    """Return a real brand string, or '' if the value is a placeholder."""
    return "" if is_placeholder(value) else (value or "").strip()


def first_real_brand(*values: str | None) -> str:
    """First non-placeholder brand across E1/Unilog/DIB, else ''."""
    for value in values:
        cleaned = clean_brand(value)
        if cleaned:
            return cleaned
    return ""
