from fastapi import APIRouter

from app.api.deps import SessionDep
from app.schemas.catalog import CatalogProduct
from app.services import catalog_service

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("", response_model=list[CatalogProduct])
async def get_catalog(session: SessionDep):
    return await catalog_service.list_published_catalog(session)
