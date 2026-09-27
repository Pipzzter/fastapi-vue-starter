from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException, status

from app.schemas.user import UserCreate
from app.services.auth import AuthService

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def mock_user_service(user_factory):
    service = Mock()
    service.get_by_email = AsyncMock(return_value=None)
    service.create_user = AsyncMock()
    return service


async def test_register_user_success(mock_user_service, monkeypatch):
    auth_service = AuthService.__new__(AuthService)
    auth_service.user_service = mock_user_service
    monkeypatch.setattr("app.services.auth.get_password_hash", lambda _: "hashed")

    payload = UserCreate(email="new@example.com", password="secret")
    mock_user_service.create_user.return_value = Mock(email=payload.email)

    result = await AuthService.register_user(auth_service, payload)

    assert result.email == payload.email
    mock_user_service.create_user.assert_awaited_once()


async def test_register_user_existing_email(mock_user_service, user_factory):
    auth_service = AuthService.__new__(AuthService)
    auth_service.user_service = mock_user_service
    mock_user_service.get_by_email.return_value = user_factory()

    payload = UserCreate(email="demo@example.com", password="secret")

    with pytest.raises(HTTPException) as exc:
        await AuthService.register_user(auth_service, payload)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


async def test_authenticate_user_success(mock_user_service, user_factory, monkeypatch):
    auth_service = AuthService.__new__(AuthService)
    auth_service.user_service = mock_user_service
    mock_user_service.get_by_email.return_value = user_factory(hashed_password="hash")
    monkeypatch.setattr("app.services.auth.verify_password", lambda raw, hashed: True)

    user = await AuthService.authenticate_user(
        auth_service, "demo@example.com", "secret"
    )

    assert user.email == "demo@example.com"


async def test_authenticate_user_invalid_credentials(
    mock_user_service, user_factory, monkeypatch
):
    auth_service = AuthService.__new__(AuthService)
    auth_service.user_service = mock_user_service
    mock_user_service.get_by_email.return_value = user_factory(hashed_password="hash")
    monkeypatch.setattr("app.services.auth.verify_password", lambda raw, hashed: False)

    with pytest.raises(HTTPException) as exc:
        await AuthService.authenticate_user(auth_service, "demo@example.com", "bad")

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


async def test_authenticate_user_missing(mock_user_service):
    auth_service = AuthService.__new__(AuthService)
    auth_service.user_service = mock_user_service
    mock_user_service.get_by_email.return_value = None

    with pytest.raises(HTTPException) as exc:
        await AuthService.authenticate_user(
            auth_service, "missing@example.com", "secret"
        )

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


async def test_generate_token(monkeypatch):
    monkeypatch.setattr(
        "app.services.auth.create_access_token", lambda user_id, expires: "token"
    )

    token = AuthService.generate_token(1)

    assert token.access_token == "token"
    assert token.token_type == "bearer"
