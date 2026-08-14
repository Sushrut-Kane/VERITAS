import secrets

from fastapi import APIRouter

from app.core.config import settings
from app.core.errors import UnauthorizedError
from app.core.security import create_access_token
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    valid_user = secrets.compare_digest(payload.username, settings.demo_username)
    valid_pass = secrets.compare_digest(payload.password, settings.demo_password)
    if not (valid_user and valid_pass):
        raise UnauthorizedError("Invalid credentials")
    return TokenResponse(access_token=create_access_token(subject=payload.username))
