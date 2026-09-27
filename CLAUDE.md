# CLAUDE.md

Guidance for Claude Code (and other AI assistants) working in this repository.

## What this is

A fullstack starter kit: **FastAPI** backend (async SQLAlchemy 2.0, JWT auth) +
**Vue 3 / TypeScript** frontend + **PostgreSQL**, containerized with Docker.
Layered backend: `router → service → model`, with Pydantic schemas at the edges.

## Commands

Run backend commands from `backend/`, frontend commands from `frontend/`.

```bash
# Backend
pip install -r requirements-dev.txt   # from repo root
cd backend && pytest                   # tests (in-memory SQLite; no Postgres needed)
ruff check backend scripts             # lint (run from repo root)
ruff format backend scripts            # format
uvicorn app.main:app --reload          # run (needs a reachable Postgres for DB routes)

# Frontend
cd frontend && npm install
npm run dev            # dev server (http://localhost:5173)
npm run build          # type-check + production build
npx eslint .           # lint

# Everything together
docker compose -f docker/docker-compose.yml up -d --build
```

## Architecture

- **Config** (`app/core/config.py`): `pydantic-settings`. Every field has a dev
  default, so the app and tests run with no `.env`. The Postgres URL is **derived**
  from `POSTGRES_*` fields — `database_url` (sync/psycopg2, for Alembic) and
  `async_database_url` (asyncpg, for the app). `get_settings()` is `lru_cache`d and
  refuses to boot in production with the default `SECRET_KEY`.
- **Request flow**: `api/v1/routers/*` (thin HTTP layer) → `services/*` (business
  logic, returns Pydantic `*Read` schemas) → `models/*` (SQLAlchemy). Routers get a
  session via `Depends(get_session)`.
- **Auth**: OAuth2 password flow. `core/security.py` (PyJWT + pwdlib/argon2) issues
  and decodes tokens; `dependencies.get_current_user` (`CurrentUser` alias) protects
  routes. Tokens carry `sub` = user id (as a string).
- **Middleware** (`middleware/__init__.py`): CORS (origins from
  `backend_cors_origins`) + request-timing header. Rate limiting via `slowapi` is
  wired in `main.py` (`app.state.limiter`) and applied per-route in the auth router.
- **DB session** (`db/session.py`): the async engine is created at import time from
  `settings.async_database_url`.

## Conventions

- **Imports**: Ruff's isort with `known-first-party = ["app"]`; stdlib →
  third-party → `app.*`. Line length 88. Let `ruff format` decide layout.
- **Typing**: modern syntax — `str | None`, `list[...]`, `datetime.UTC`. Target
  Python ≥ 3.11.
- **Do not reintroduce** `python-jose` or `pydantic.v1` shims — both were removed
  deliberately (use `PyJWT` and Pydantic v2 `EmailStr`).
- Keep routers thin; put logic in services. Services return schemas, not ORM models.

### Adding a new entity (the pattern to follow)

1. `models/<name>.py` — SQLAlchemy model (`Mapped[...] = mapped_column(...)`).
2. `schemas/<name>.py` — `Base`/`Create`/`Read` Pydantic models
   (`model_config = ConfigDict(from_attributes=True)` on `Read`).
3. `services/<name>.py` — a service class taking `AsyncSession`.
4. `api/v1/routers/<name>.py` — routes; register it in `api/v1/routers/__init__.py`.
5. Migration: `cd backend && alembic revision --autogenerate -m "add <name>"`.
6. Tests under `tests/` mirroring the package path.

## Testing

- `pytest-asyncio` in `auto` mode; tests use an in-memory SQLite engine and
  `app.dependency_overrides[get_session]` (see `tests/conftest.py`).
- Router tests mock the service layer; protected routes are unlocked with the
  `current_user` fixture (overrides `get_current_user`). Add both an authorized and
  an unauthorized test when adding a protected route.
- Add a test with every change; CI treats a failing suite as a hard failure.

## Gotchas

- Importing the app instantiates the async engine, so `asyncpg` must be installed
  (it is, via `requirements.txt`) even for the SQLite-backed tests.
- `docker/backend/entrypoint.sh` runs `alembic upgrade head` before uvicorn and
  **must stay LF-terminated** (enforced by `.gitattributes`) or it breaks in the
  Linux container.
- Inside Docker Compose, `POSTGRES_SERVER` is overridden to `db`; locally it is
  `localhost`. Don't hardcode a `DATABASE_URL` in `.env` unless you mean to override
  both.
- Dependencies are pinned in `requirements*.txt`; bump deliberately and re-run tests.
