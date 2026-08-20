"""Formula-driven description builders with char-limit enforcement.

Modeled on the two worked Delivery-Format examples:
- INVOICE_DESC: <=40 chars, UPPERCASE, abbreviated.
- MOBILE_DESC:  60-80 chars, "{mfr/brand}, {product}, {series}, {part#}".
- SHORT_DESC:   brand + series + part# + product + key attributes.
- RETAIL_DESC:  like SHORT but without brand/part number.
- LONG_DESC1:   full attribute rollup.
"""
import re

from app.catalog.models import EnrichedProduct
from app.catalog.uom import canonical_uom, format_quantity

INVOICE_MAX = 40
MOBILE_MIN, MOBILE_MAX = 60, 80

_VALUE_ABBR = {
    "stainless steel": "SST",
    "built-in": "BLTLN",
    "built in": "BLTLN",
    "leg": "LEG",
    "professional series": "PRO",
}


def _truncate(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rstrip()
    if " " in cut:
        cut = cut[: cut.rfind(" ")].rstrip()
    return cut


def _shorten_label(label: str) -> str:
    label = re.sub(r"^Number of\s+", "", label)
    label = re.sub(r"\s+Type$", "", label)
    return label.strip()


def _content_attrs(product: EnrichedProduct):
    return [
        a
        for a in product.attributes
        if a.label not in {"Type", "Additional Information"} and (a.value or "").strip()
    ]


def _attr_phrase(attr) -> str:
    if attr.uom:
        return format_quantity(attr.value, attr.uom)
    return f"{attr.value} {_shorten_label(attr.label)}".strip()


def _invoice_token(attr) -> str:
    value = (attr.value or "").strip()
    if attr.uom:
        return f"{value}{canonical_uom(attr.uom)}".upper().replace(" ", "")
    return _VALUE_ABBR.get(value.lower(), value.upper())


def build_invoice_desc(product: EnrichedProduct) -> str:
    tokens = [product.product_type.upper()] if product.product_type else []
    tokens += [_invoice_token(a) for a in _content_attrs(product)]
    return _truncate(" ".join(t for t in tokens if t), INVOICE_MAX)


def build_mobile_desc(product: EnrichedProduct) -> str:
    lead = product.manufacturer_name or product.brand_name
    segments: list[str] = []
    if lead and product.brand_name and product.brand_name != lead:
        segments.append(f"{lead} {product.brand_name}")
    elif lead:
        segments.append(lead)
    if product.product_type:
        segments.append(product.product_type)
    if product.series:
        segments.append(product.series)
    if product.part_number:
        segments.append(product.part_number)

    text = ", ".join(segments)
    if len(text) < MOBILE_MIN:
        for attr in _content_attrs(product):
            text = f"{text}, {_attr_phrase(attr)}"
            if len(text) >= MOBILE_MIN:
                break
    return _truncate(text, MOBILE_MAX)


def build_short_desc(product: EnrichedProduct) -> str:
    head = " ".join(
        p
        for p in (product.brand_name, product.series, product.part_number, product.product_type)
        if p
    )
    tail = ", ".join(_attr_phrase(a) for a in _content_attrs(product))
    return f"{head}, {tail}".strip(", ") if tail else head


def build_retail_desc(product: EnrichedProduct) -> str:
    head = " ".join(p for p in (product.series, product.product_type) if p)
    tail = ", ".join(_attr_phrase(a) for a in _content_attrs(product))
    return f"{head}, {tail}".strip(", ") if tail else head


def build_long_desc(product: EnrichedProduct) -> str:
    head = " ".join(p for p in (product.brand_name, product.product_type) if p)
    if product.item_features:
        head = f"{head} With {', '.join(product.item_features)}"
    parts = [head] if head else []
    if product.series:
        parts.append(product.series)
    parts.extend(_attr_phrase(a) for a in _content_attrs(product))
    additional = next(
        (a.value for a in product.attributes if a.label == "Additional Information"),
        "",
    )
    text = ", ".join(p for p in parts if p)
    if additional:
        text = f"{text}, Additional Information: {additional}"
    return text


def build_product_name(product: EnrichedProduct) -> str:
    return product.product_type


def build_all(product: EnrichedProduct) -> EnrichedProduct:
    product.invoice_desc = build_invoice_desc(product)
    product.mobile_desc = build_mobile_desc(product)
    product.short_desc = build_short_desc(product)
    product.retail_desc = build_retail_desc(product)
    product.long_desc = build_long_desc(product)
    product.product_name = build_product_name(product)
    return product
