import logging

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter
from app.db.session import get_session
from app.dependencies import CurrentUser
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserRead
from app.services.auth import AuthService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def register_user(
    request: Request,
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> Token:
    auth_service = AuthService(session)
    logger.debug("Registering new user %s", payload.email)
    user = await auth_service.register_user(payload)
    return auth_service.generate_token(user.id)


@router.post("/token", response_model=Token)
@limiter.limit("10/minute")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
) -> Token:
    auth_service = AuthService(session)
    logger.debug("Authenticating user %s", form_data.username)
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    return auth_service.generate_token(user.id)


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)
