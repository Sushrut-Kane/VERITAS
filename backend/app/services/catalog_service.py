from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.attribute import Attribute, PolicyDecision
from app.db.models.product import Product


async def list_published_catalog(session: AsyncSession) -> list[dict]:
    """Published attributes grouped by product."""
    stmt = (
        select(Attribute, Product.sku, Product.name)
        .join(Product, Attribute.product_id == Product.id)
        .where(Attribute.policy_decision == PolicyDecision.publish)
        .order_by(Product.sku, Attribute.attr_key)
    )
    result = await session.execute(stmt)

    catalog: dict[str, dict] = {}
    for attribute, sku, name in result.all():
        entry = catalog.setdefault(sku, {"sku": sku, "name": name, "attributes": []})
        entry["attributes"].append(attribute)
    return list(catalog.values())
