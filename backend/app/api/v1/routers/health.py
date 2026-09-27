import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.health import HealthResponse
from app.services.health import HealthService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=HealthResponse, summary="Liveness check")
async def health_check() -> HealthResponse:
    status = await HealthService().get_status()
    logger.debug("Health check status: %s", status)
    return HealthResponse(**status)


@router.get("/ready", summary="Readiness check (verifies database connectivity)")
async def readiness_check(
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    await session.execute(text("SELECT 1"))
    return {"status": "ready"}
