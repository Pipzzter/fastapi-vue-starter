from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.middleware.request_timing import RequestTimingMiddleware


def register_middlewares(app: FastAPI) -> None:
    settings = get_settings()

    if settings.backend_cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.backend_cors_origins],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    if not any(m.cls is RequestTimingMiddleware for m in app.user_middleware):
        app.add_middleware(RequestTimingMiddleware)
