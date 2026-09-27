import pytest

from app.services.health import HealthService

pytestmark = pytest.mark.asyncio


async def test_health_status_contains_expected_keys(monkeypatch):
    class _FakeDatetime:
        @staticmethod
        def now(_timezone):
            return "2024-01-01T00:00:00Z"

    monkeypatch.setattr("app.services.health.datetime", _FakeDatetime)

    result = await HealthService.get_status()

    assert result["status"] == "ok"
    assert result["timestamp"] == "2024-01-01T00:00:00Z"
