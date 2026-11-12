# Infrastructure Architecture

Phase 1 provides a four-service local stack for the existing React dashboard and a minimal FastAPI service. It intentionally defines no supply-chain domain models or business behavior.

## Services and communication

| Service | Image/build | Container port | Host port | Purpose |
| --- | --- | ---: | ---: | --- |
| PostgreSQL | `postgres:16-alpine` | 5432 | `POSTGRES_PORT` (5432) | Persistent relational database |
| Redis | `redis:7-alpine` | 6379 | `REDIS_PORT` (6379) | Cache and future queue/broker infrastructure; AOF persistence is enabled |
| Backend | `backend/Dockerfile` (Python 3.12) | 8000 | `BACKEND_PORT` (8000) | FastAPI API and Alembic migration environment |
| Frontend | `frontend/Dockerfile` (Node build, Nginx runtime) | 80 | `FRONTEND_PORT` (3000) | Existing React/Vite production build |

Compose service DNS names are used for container-to-container connections. The backend reaches PostgreSQL at `postgres:5432` and Redis at `redis:6379`; the frontend is published on the host and its service startup waits for backend health. PostgreSQL and Redis health checks gate backend startup. The API health route reports process/application availability only; database and Redis are separately gated by their Compose health checks.

## Configuration and persistence

Copy the root `.env.example` to `.env` before starting Compose. Compose requires both `POSTGRES_PASSWORD` and `JWT_SECRET_KEY`; it will fail fast if either is missing. Generate URL-safe local secrets rather than using the example placeholders:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(24))"
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Use the first output for `POSTGRES_PASSWORD` and the second for `JWT_SECRET_KEY`. The password is URL-safe so it can be embedded in the backend's PostgreSQL connection URL. Never commit `.env` or place real secrets in source control. The backend settings load repository-root `.env` and, for standalone backend runs, `backend/.env`; environment variables supplied by Compose or the deployment environment take precedence.

Named volumes `postgres_data` and `redis_data` preserve database files across container recreation. Redis uses append-only-file persistence.

## Startup

Run `docker compose up --build` from the repository root after creating and populating `.env`. The API is available at `http://localhost:8000` and `http://localhost:8000/health`; the frontend is at `http://localhost:3000`. Override published ports through `.env` when those ports are occupied. Stop the stack with `docker compose down`; persistent data remains in named volumes. `docker compose down -v` removes that data.

Alembic is configured in `backend/alembic.ini` and reads the same validated `DATABASE_URL` setting as the application. From the backend environment, use `alembic upgrade head` to apply migrations and `alembic downgrade -1` to reverse one revision. Phase 2 adds the supply-chain schema; see [the data model](../database/erd.md).

## Container hardening

The backend image runs as an unprivileged user. Build contexts exclude local virtual environments, environment files, Git metadata, tests, and coverage output. Demo login credentials are for local demonstrations only and are not suitable for production authentication.

## CI

`.github/workflows/ci.yml` runs on pushes to `main` and pull requests targeting `main`. Backend checks install the project and dev tools, then run Ruff, Black, Mypy, Alembic migration, and Pytest checks. Frontend checks install from the npm lockfile, run TypeScript project checks, and build the production bundle. The Docker job validates Compose and builds both application images using disposable CI-only secrets.
