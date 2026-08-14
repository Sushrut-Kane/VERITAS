"""§3.1  POST /products
§3.4  GET /products/{product_id}/attributes
"""
import uuid

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, SessionDep
from app.schemas.attribute import AttributeRead, ProductAttributesResponse
from app.schemas.product import ProductCreate, ProductRead
from app.services import attribute_service, product_service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductRead])
async def list_products(session: SessionDep):
    return await product_service.list_products(session)


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate, session: SessionDep, _: CurrentUser):
    return await product_service.create_product(session, payload)


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: uuid.UUID, session: SessionDep):
    return await product_service.get_product(session, product_id)


@router.get("/{product_id}/attributes", response_model=ProductAttributesResponse)
async def list_product_attributes(product_id: uuid.UUID, session: SessionDep):
    """§3.4 — wrapped response with source_count per attribute."""
    await product_service.get_product(session, product_id)  # 404 if missing
    rows = await attribute_service.list_attributes_for_product(session, product_id)
    items = [
        AttributeRead(
            id=a.id,
            attr_key=a.attr_key,
            attr_value=a.attr_value,
            classification=a.classification,
            classification_confidence=a.classification_confidence,
            policy_decision=a.policy_decision,
            source_count=await attribute_service.count_sources(session, a.id),
        )
        for a in rows
    ]
    return ProductAttributesResponse(product_id=product_id, attributes=items)
