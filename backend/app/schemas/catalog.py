from pydantic import BaseModel

from app.schemas.attribute import AttributeRead


class CatalogProduct(BaseModel):
    sku: str
    name: str | None = None
    attributes: list[AttributeRead]
