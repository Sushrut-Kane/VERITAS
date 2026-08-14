import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.db.models.attribute import Attribute
from app.db.models.product import Product
from app.graph import queries


async def get_attribute(session: AsyncSession, attribute_id: uuid.UUID) -> Attribute:
    attribute = await session.get(Attribute, attribute_id)
    if attribute is None:
        raise NotFoundError(f"Attribute {attribute_id} not found")
    return attribute


async def list_attributes_for_product(
    session: AsyncSession, product_id: uuid.UUID
) -> list[Attribute]:
    result = await session.execute(
        select(Attribute)
        .where(Attribute.product_id == product_id)
        .order_by(Attribute.attr_key, Attribute.created_at.desc())
    )
    return list(result.scalars().all())


async def get_attribute_graph(
    session: AsyncSession, attribute_id: uuid.UUID
) -> dict:
    attribute = await get_attribute(session, attribute_id)
    product = await session.get(Product, attribute.product_id)
    if product is None:
        raise NotFoundError(f"Product for attribute {attribute_id} not found")
    subgraph = await queries.attribute_evidence_subgraph(product.sku, attribute.attr_key)
    return {
        "attribute_id": attribute.id,
        "attr_key": attribute.attr_key,
        "nodes": subgraph["nodes"],
        "edges": subgraph["edges"],
    }
