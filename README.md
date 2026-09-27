# FastAPI + Vue Starter

A production-ready fullstack starter kit: a **FastAPI** backend with JWT auth and
async SQLAlchemy, a **Vue 3 + TypeScript** frontend, **PostgreSQL**, and a
Docker-first workflow with migrations, linting, tests, and CI wired up.

> Clone it, run one command, and you have a working authenticated API + SPA.

## Features

- **FastAPI** with a clean layered architecture (routers → services → models).
- **JWT authentication** — register, login, and a protected `/me` endpoint using
  OAuth2 password flow, Argon2 password hashing (`pwdlib`), and `PyJWT`.
- **Async SQLAlchemy 2.0** (asyncpg) with **Alembic** migrations that run
  automatically on container start.
- **Type-safe settings** via `pydantic-settings` — sensible defaults for local
  dev, environment-driven for staging/production.
- **CORS**, **request-timing middleware**, and **rate limiting** (`slowapi`) on
  auth endpoints.
- **Liveness & readiness** health checks (the readiness probe verifies the DB).
- **Vue 3 + Vite + Pinia + Vue Router + TypeScript** frontend with an example
  view that live-checks the backend.
- **Tooling**: Ruff (lint + format + import sorting), pre-commit hooks, a pytest
  suite, and a **GitHub Actions CI** pipeline.
- **Docker Compose** for one-command local development.

## Tech stack

| Layer     | Choices                                                        |
| --------- | -------------------------------------------------------------- |
| Backend   | FastAPI, SQLAlchemy 2.0 (async), Alembic, pydantic-settings    |
| Auth      | PyJWT, pwdlib[argon2], OAuth2 password flow                    |
| Database  | PostgreSQL (asyncpg at runtime, psycopg2 for migrations)       |
| Frontend  | Vue 3, TypeScript, Vite, Pinia, Vue Router                     |
| Tooling   | Ruff, pre-commit, pytest, GitHub Actions                       |
| Infra     | Docker, Docker Compose, Nginx (production frontend)            |

## Project structure

```
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/v1/routers/   # HTTP routes (auth, user, health)
│   │   ├── core/             # config, security, logging, limiter
│   │   ├── db/               # engine, session, declarative base
│   │   ├── middleware/       # CORS + request timing
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic request/response models
│   │   ├── services/         # business logic
│   │   ├── dependencies.py   # shared deps (auth, DB session)
│   │   └── main.py           # app factory
│   ├── alembic/              # migrations
│   └── tests/                # pytest suite
├── frontend/                # Vue 3 + Vite application
├── docker/                  # Dockerfiles, compose, nginx, entrypoint
├── scripts/                 # utility scripts
├── pyproject.toml           # Ruff + project metadata
└── .github/workflows/       # CI
```

## Quick start (Docker)

The fastest path — spins up the API, frontend, and Postgres, and applies
migrations automatically.

```bash
cp backend/.env.example backend/.env      # optional: defaults work out of the box
docker compose -f docker/docker-compose.yml up -d --build
```

- Frontend: http://localhost:5173
- API docs (Swagger): http://localhost:8000/api/v1/docs
- API health: http://localhost:8000/api/v1/health/

Stop with `docker compose -f docker/docker-compose.yml down` (add `-v` to also
drop the database volume).

## Local development (without Docker)

### Backend

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

# Start a Postgres for the app (or use the compose "db" service), then:
cp backend/.env.example backend/.env
cd backend
alembic upgrade head
uvicorn app.main:app --reload
```

The app boots with development defaults even without a `.env`, but the database
endpoints need a reachable Postgres.

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

## Environment configuration

All settings live in `backend/.env` (see `backend/.env.example`). Every value has
a development default in `app/core/config.py`, so the project runs and its tests
pass with no `.env`. The Postgres connection URL is **derived** from the
`POSTGRES_*` variables; under Docker Compose, `POSTGRES_SERVER` is overridden to
the `db` service automatically.

> **Production:** set a strong `SECRET_KEY` and `ENVIRONMENT=production`. The app
> refuses to start in production while the default secret is in place.

## API reference

| Method & path                | Auth   | Description                          |
| ---------------------------- | ------ | ------------------------------------ |
| `GET  /api/v1/health/`       | –      | Liveness check                       |
| `GET  /api/v1/health/ready`  | –      | Readiness check (verifies the DB)    |
| `POST /api/v1/auth/register` | –      | Register a user, returns a JWT       |
| `POST /api/v1/auth/token`    | –      | Login (OAuth2 form), returns a JWT   |
| `GET  /api/v1/auth/me`       | Bearer | Current authenticated user           |
| `POST /api/v1/user/`         | –      | Create a user                        |
| `GET  /api/v1/user/`         | Bearer | List users                           |

Example:

```bash
# Register and capture the token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"me@example.com","password":"secret","full_name":"Me"}' \
  | python -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

# Call a protected endpoint
curl http://localhost:8000/api/v1/auth/me -H "Authorization: Bearer $TOKEN"
```

## Tests

```bash
cd backend
pytest                 # full suite (uses in-memory SQLite, no Postgres needed)
pytest tests/services  # a subset
```

## Linting, formatting & pre-commit

Ruff handles linting, formatting, and import sorting; configuration lives in
`pyproject.toml`.

```bash
ruff check backend scripts      # lint
ruff format backend scripts     # format
```

Install the git hooks (format + lint on commit, plus pytest for changed test
files):

```bash
pre-commit install
pre-commit run --all-files      # optional warm-up
```

## Environments & Docker targets

Set `APP_ENV` to pick the Docker multi-stage target:

```bash
# development (default) — hot reload, dev dependencies
docker compose -f docker/docker-compose.yml up -d

# staging / production images
APP_ENV=production docker compose -f docker/docker-compose.yml up -d --build
```

The frontend Compose service always runs the Vite dev server; the `production`
frontend stage builds a static bundle served by Nginx and is intended for your
deployment pipeline rather than local Compose.

## Continuous integration

`.github/workflows/ci.yml` runs on every push and pull request:

- **Backend** — Ruff lint, Ruff format check, and pytest.
- **Frontend** — ESLint, `vue-tsc` type-check, and a production build.

## License

[MIT](LICENSE)
