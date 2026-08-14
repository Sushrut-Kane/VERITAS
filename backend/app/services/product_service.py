import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, NotFoundError
from app.db.models.product import Product
from app.schemas.product import ProductCreate


async def get_product_by_sku(session: AsyncSession, sku: str) -> Product | None:
    result = await session.execute(select(Product).where(Product.sku == sku))
    return result.scalar_one_or_none()


async def get_product(session: AsyncSession, product_id: uuid.UUID) -> Product:
    product = await session.get(Product, product_id)
    if product is None:
        raise NotFoundError(f"Product {product_id} not found")
    return product


async def list_products(session: AsyncSession) -> list[Product]:
    result = await session.execute(select(Product).order_by(Product.created_at.desc()))
    return list(result.scalars().all())


async def create_product(session: AsyncSession, data: ProductCreate) -> Product:
    if await get_product_by_sku(session, data.sku) is not None:
        raise ConflictError(f"Product with sku '{data.sku}' already exists")
    product = Product(sku=data.sku, name=data.name)
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


async def get_or_create_product(
    session: AsyncSession, sku: str, name: str | None = None
) -> Product:
    existing = await get_product_by_sku(session, sku)
    if existing is not None:
        return existing
    product = Product(sku=sku, name=name)
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product
