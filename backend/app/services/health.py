import logging
from datetime import UTC, datetime

logger = logging.getLogger(__name__)


class HealthService:
    @staticmethod
    async def get_status() -> dict:
        status = {"status": "ok", "timestamp": datetime.now(UTC)}
        logger.debug("Generated health status %s", status)
        return status
