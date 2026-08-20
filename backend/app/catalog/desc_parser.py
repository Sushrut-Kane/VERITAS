"""Deterministic attribute extraction from a free-text ``Part_Desc``.

Tuned for the abrasives / cutting-tool rows that dominate the sample dataset
(dimensions in inches with fractions, grit, pack quantity, product type). Returns
structured attributes plus a best-guess product type. No LLM required; an LLM
pass (when a key is configured) can enrich on top of this baseline.
"""
import re

from app.catalog.models import Attribute

# A single numeric token: mixed fraction, simple fraction, decimal, leading-dot
# decimal, or integer (order matters — longest alternatives first).
_NUM = r"\d+-\d+/\d+|\d+/\d+|\d+\.\d+|\.\d+|\d+"
_MEAS = rf'(?:{_NUM})\s*"?'
_DIM_GROUP_RE = re.compile(rf'({_MEAS}(?:\s*[xX]\s*{_MEAS})+)')
_GRIT_RE = re.compile(r"\b(P\d{2,4}|\d{2,4}\s*[Gg]rit)\b")
_PACK_RE = re.compile(
    r"\b(\d+)\s*(Disc/Box|Disc|Box|pcs|pc|pk|pack|ct)\b", re.IGNORECASE
)

_DISC_LABELS_3 = ["Diameter", "Thickness", "Arbor Size"]
_DISC_LABELS_2 = ["Width", "Length"]


def _clean_leading_part_number(text: str, part_number: str) -> str:
    stripped = text.strip()
    if part_number and stripped.upper().startswith(part_number.upper()):
        stripped = stripped[len(part_number):].strip(" -")
    return stripped


def _extract_dimensions(text: str) -> tuple[list[Attribute], str]:
    match = _DIM_GROUP_RE.search(text)
    if not match:
        return [], text
    raw = match.group(1)
    dims = [d.strip().strip('"').strip() for d in re.split(r"[xX]", raw) if d.strip()]
    if len(dims) == 3:
        labels = _DISC_LABELS_3
    elif len(dims) == 2:
        labels = _DISC_LABELS_2
    else:
        labels = ["Size"]
    attributes = [
        Attribute(labels[i] if i < len(labels) else f"Dimension {i + 1}", dim, "in")
        for i, dim in enumerate(dims)
    ]
    remainder = (text[: match.start()] + " " + text[match.end():]).strip()
    return attributes, remainder


def parse_part_desc(
    part_desc: str, part_number: str = ""
) -> tuple[list[Attribute], str]:
    """Return ``(attributes, product_type)`` parsed from a description string."""
    text = _clean_leading_part_number(part_desc, part_number)
    attributes: list[Attribute] = []

    grit_match = _GRIT_RE.search(text)
    if grit_match:
        attributes.append(Attribute("Grit", grit_match.group(1).replace(" ", "")))
        text = (text[: grit_match.start()] + " " + text[grit_match.end():]).strip()

    pack_match = _PACK_RE.search(text)
    if pack_match:
        qty, unit = pack_match.group(1), pack_match.group(2)
        uom = "pc" if unit.lower() in {"pc", "pcs", "pk", "pack"} else unit
        attributes.append(Attribute("Package Quantity", qty, uom))
        text = (text[: pack_match.start()] + " " + text[pack_match.end():]).strip()

    dim_attrs, text = _extract_dimensions(text)
    attributes.extend(dim_attrs)

    # Whatever readable text remains is the product-type descriptor.
    product_type = re.sub(r"\s{2,}", " ", text).strip(" -,")
    product_type = re.sub(r"\s*-\s*", " ", product_type).strip()
    return attributes, product_type
