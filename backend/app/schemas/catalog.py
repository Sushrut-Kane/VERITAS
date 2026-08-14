"""Pydantic schemas for the catalog endpoint (§3.9)."""

from pydantic import BaseModel


class CatalogAttribute(BaseModel):
    attr_key: str
    attr_value: str
    trust_badge: str  # "verified", "derived", "inferred", "conflicting"


class CatalogProduct(BaseModel):
    sku: str
    name: str | None = None
    attributes: list[CatalogAttribute]


class CatalogResponse(BaseModel):
    products: list[CatalogProduct]
