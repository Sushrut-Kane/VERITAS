"""Turn a raw CatalogRow into an EnrichedProduct (deterministic, stdlib-only).

An optional LLM enrichment pass lives in app.catalog.llm_enrich and is invoked
only by callers that opt in (e.g. the API), so importing this module never
requires an API key or third-party packages.
"""
import re

from app.catalog.desc_parser import parse_part_desc
from app.catalog.descriptions import build_all
from app.catalog.manufacturer import parse_manufacturer
from app.catalog.models import Attribute, CatalogRow, EnrichedProduct
from app.catalog.placeholder import first_real_brand


def _root(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _strip_leading_brand(product_type: str, manufacturer_name: str) -> str:
    tokens = product_type.split()
    if not tokens:
        return product_type
    first = _root(tokens[0])
    mfr_tokens = [_root(t) for t in manufacturer_name.split() if len(t) > 2]
    if first and any(t.startswith(first) or first.startswith(t) for t in mfr_tokens):
        return " ".join(tokens[1:]).strip()
    return product_type


def _brand_manufacturer_mismatch(brand: str, manufacturer: str) -> bool:
    if not brand or not manufacturer:
        return False
    brand_root = _root(brand)
    mfr_tokens = [_root(t) for t in manufacturer.split() if t]
    return not any(
        brand_root and (brand_root in t or t in brand_root) for t in mfr_tokens
    )


def enrich_row(row: CatalogRow) -> EnrichedProduct:
    name, code = parse_manufacturer(row.part_manuf)
    brand = first_real_brand(row.unilog_brand, row.e1_brand, row.dib_brand)
    attributes, product_type = parse_part_desc(row.part_desc, row.mfg_part_num)
    product_type = _strip_leading_brand(product_type, name)
    if product_type:
        attributes.append(Attribute("Type", product_type))

    product = EnrichedProduct(
        part_number=row.mfg_part_num,
        part_desc=row.part_desc,
        manufacturer_name=name,
        manufacturer_code=code,
        brand_name=brand,
        product_type=product_type,
        attributes=attributes,
    )
    if _brand_manufacturer_mismatch(brand, name):
        product.needs_review = True
        product.review_reasons.append(
            "manufacturer/brand pairing not found in approved list — "
            "confirm OEM/licensing relationship"
        )
    return build_all(product)
