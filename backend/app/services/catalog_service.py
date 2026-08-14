"""Service layer for the catalog endpoint (§3.9)."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.attribute import Attribute, Classification, PolicyDecision
from app.db.models.product import Product
from app.schemas.catalog import CatalogAttribute, CatalogProduct, CatalogResponse


def _trust_badge(classification: Classification | None) -> str:
    """Map classification to trust_badge for the catalog view."""
    if classification is None:
        return "verified"
    return classification.value  # verified, derived, inferred, conflicting


async def list_published_catalog(session: AsyncSession) -> CatalogResponse:
    """§3.9 — published attributes grouped by product with trust badges."""
    stmt = (
        select(Attribute, Product.sku, Product.name)
        .join(Product, Attribute.product_id == Product.id)
        .where(Attribute.policy_decision == PolicyDecision.publish)
        .order_by(Product.sku, Attribute.attr_key)
    )
    result = await session.execute(stmt)

    catalog: dict[str, CatalogProduct] = {}
    for attribute, sku, name in result.all():
        if sku not in catalog:
            catalog[sku] = CatalogProduct(sku=sku, name=name, attributes=[])
        catalog[sku].attributes.append(
            CatalogAttribute(
                attr_key=attribute.attr_key,
                attr_value=attribute.attr_value,
                trust_badge=_trust_badge(attribute.classification),
            )
        )
    return CatalogResponse(products=list(catalog.values()))
