"""Optional LLM enrichment for a catalog row.

Used only when a caller opts in AND an API key is configured. Constrained: the
model may only ADD attributes / features / a product type implied by the part
description — it must never invent a manufacturer or brand. Any failure falls
back silently to the deterministic product, so callers always get a valid result.
"""
import json

from app.agents import llm
from app.catalog.descriptions import build_all
from app.catalog.models import Attribute, CatalogRow, EnrichedProduct
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_SYSTEM = (
    "You enrich a single industrial-catalog product record. "
    "Return ONLY JSON: "
    '{"product_type": str, "attributes": [{"label": str, "value": str, "uom": str}], '
    '"item_features": [str]}. '
    "Use only facts stated or strongly implied by the part description; if unsure, omit. "
    "Never invent a manufacturer, brand, price, or certification."
)


def _merge_attributes(
    existing: list[Attribute], new_items: list[dict]
) -> list[Attribute]:
    seen = {a.label.strip().lower() for a in existing}
    merged = list(existing)
    for item in new_items:
        label = str(item.get("label", "")).strip()
        value = str(item.get("value", "")).strip()
        if not label or not value or label.lower() in seen:
            continue
        merged.append(Attribute(label, value, str(item.get("uom", "")).strip()))
        seen.add(label.lower())
    return merged


async def llm_enrich_product(
    row: CatalogRow, product: EnrichedProduct
) -> EnrichedProduct:
    if not settings.llm_enabled:
        return product
    prompt = (
        f"Part number: {row.mfg_part_num}\n"
        f"Description: {row.part_desc}\n"
        f"Manufacturer: {product.manufacturer_name}\n"
        "Enrich this product. Respond with the JSON object only."
    )
    try:
        raw = await llm.complete(_SYSTEM, prompt)
        data = llm.parse_json_block(raw)
    except Exception as exc:  # offline / rate-limited / malformed — keep deterministic
        logger.warning("llm_enrich_failed", part=row.mfg_part_num, error=str(exc))
        return product

    if isinstance(data, dict):
        if not product.product_type and data.get("product_type"):
            product.product_type = str(data["product_type"]).strip()
        product.attributes = _merge_attributes(
            product.attributes, data.get("attributes", []) or []
        )
        features = [str(f).strip() for f in data.get("item_features", []) or [] if f]
        if features:
            product.item_features = features[:20]
    return build_all(product)
