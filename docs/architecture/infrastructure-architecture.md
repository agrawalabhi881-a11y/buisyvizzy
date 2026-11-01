# Infrastructure Architecture

Phase 1 provides a four-service local stack for the existing React dashboard and a minimal FastAPI service. It intentionally defines no supply-chain domain models or business behavior.

## Services and communication

| Service | Image/build | Container port | Host port | Purpose |
| --- | --- | ---: | ---: | --- |
| PostgreSQL | `postgres:16-alpine` | 5432 | `POSTGRES_PORT` (5432) | Persistent relational database |
| Redis | `redis:7-alpine` | 6379 | `REDIS_PORT` (6379) | Cache and future queue/broker infrastructure; AOF persistence is enabled |
| Backend | `backend/Dockerfile` (Python 3.12) | 8000 | `BACKEND_PORT` (8000) | FastAPI API and Alembic migration environment |
| Frontend | `frontend/Dockerfile` (Node build, Nginx runtime) | 80 | `FRONTEND_PORT` (3000) | Existing React/Vite production build |

Compose service DNS names are used for container-to-container connections. The backend reaches PostgreSQL at `postgres:5432` and Redis at `redis:6379`; the frontend is published on the host and its service startup waits for backend health. PostgreSQL and Redis health checks gate backend startup. The API health route reports only application status and does not assert database or Redis connectivity.

## Configuration and persistence

Copy `.env.example` to `.env` for local overrides. Compose reads PostgreSQL credentials, host ports, and application environment from these variables. `DATABASE_URL` is available for local backend tools and Alembic; Compose constructs the container URL with the database service hostname. The example credential is a development placeholder and should be replaced for local use. Do not put secrets in source control.

Named volumes `postgres_data` and `redis_data` preserve database files across container recreation. Redis uses append-only-file persistence.

## Startup

Run `docker compose up --build` from the repository root. The API is available at `http://localhost:8000` and `http://localhost:8000/health`; the frontend is at `http://localhost:3000`. Override published ports through `.env` when those ports are occupied. Stop the stack with `docker compose down`; persistent data remains in named volumes. `docker compose down -v` removes that data.

Alembic is configured in `backend/alembic.ini` and reads `DATABASE_URL`. From the backend environment, use `alembic upgrade head` to apply migrations and `alembic downgrade -1` to reverse one revision. Phase 2 adds the supply-chain schema; see [the data model](../database/erd.md).

## CI

`.github/workflows/ci.yml` runs on pushes to `main` and pull requests targeting `main`. Backend checks install the project and dev tools, then run Ruff, Black, Mypy, and Pytest. Frontend checks install from the npm lockfile, run TypeScript project checks, and build the production bundle. The Docker job validates Compose and builds both application images. No production credentials are needed by these jobs.
