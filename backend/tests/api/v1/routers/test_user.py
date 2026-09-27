import pytest
from fastapi import status
from httpx import AsyncClient

from app.schemas.user import UserRead


@pytest.mark.asyncio
async def test_create_user_success(async_client: AsyncClient, mock_user_service):
    payload = {"email": "test@example.com", "password": "StrongPass123"}
    mock_user_service.create_user.return_value = UserRead(
        id=1, email=payload["email"], full_name=None
    )

    response = await async_client.post("/api/v1/user/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == payload["email"]
    mock_user_service.get_by_email.assert_awaited_once_with(payload["email"])
    mock_user_service.create_user.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_user_duplicate_email(
    async_client: AsyncClient, mock_user_service
):
    mock_user_service.get_by_email.return_value = object()
    payload = {"email": "duplicate@example.com", "password": "StrongPass123"}

    response = await async_client.post("/api/v1/user/", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_create_user_validation_error(
    async_client: AsyncClient, mock_user_service
):
    payload = {"password": "123"}

    response = await async_client.post("/api/v1/user/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    mock_user_service.get_by_email.assert_not_called()


@pytest.mark.asyncio
async def test_list_users(async_client: AsyncClient, mock_user_service, current_user):
    expected = [UserRead(id=1, email="one@example.com", full_name="One").model_dump()]
    mock_user_service.list_users.return_value = expected

    response = await async_client.get("/api/v1/user/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected
    mock_user_service.list_users.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_users_requires_auth(async_client: AsyncClient, mock_user_service):
    response = await async_client.get("/api/v1/user/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    mock_user_service.list_users.assert_not_called()
