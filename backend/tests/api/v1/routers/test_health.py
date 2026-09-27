import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_router(async_client: AsyncClient, mock_health_service):
    mock_health_service.get_status.return_value = {
        "status": "ok",
        "timestamp": "2025-01-01T00:00:00Z",
    }

    response = await async_client.get("/api/v1/health/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "ok"
    assert "timestamp" in response.json()
    mock_health_service.get_status.assert_awaited_once()


@pytest.mark.asyncio
async def test_readiness_check_router(async_client: AsyncClient):
    response = await async_client.get("/api/v1/health/ready")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ready"}
