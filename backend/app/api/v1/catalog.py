"""§3.9  GET /catalog
Published-only view with trust_badge per attribute.
"""
from fastapi import APIRouter

from app.api.deps import SessionDep
from app.schemas.catalog import CatalogResponse
from app.services import catalog_service

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("", response_model=CatalogResponse)
async def get_catalog(session: SessionDep):
    """§3.9 — published attributes grouped by product with trust badges."""
    return await catalog_service.list_published_catalog(session)
