# Supply Chain Digital Twin

An AI-powered supply chain simulation and decision-support platform for exploring demand uncertainty, inventory risk, logistics disruptions, and recovery strategies.

The project combines a React dashboard with a FastAPI backend and a simulation-oriented architecture. Its goal is to make supply-chain operations observable and experimentally testable: users can inspect a network, introduce a disruption, understand its operational impact, evaluate a response, and compare outcomes.

> **Project status:** Active development. The repository is being built in stages. Infrastructure, authentication, API foundations, and the dashboard are being developed ahead of the complete end-to-end supply-chain workflow. Treat scenario values and screenshots as demonstration data unless they are explicitly returned by the running backend.

---

## Contents

- [Why this project?](#why-this-project)
- [What the platform is designed to do](#what-the-platform-is-designed-to-do)
- [End-to-end demonstration workflow](#end-to-end-demonstration-workflow)
- [System architecture](#system-architecture)
- [Technology stack](#technology-stack)
- [User roles](#user-roles)
- [Repository structure](#repository-structure)
- [Getting started](#getting-started)
- [Running without Docker](#running-without-docker)
- [Database migrations](#database-migrations)
- [API overview](#api-overview)
- [Testing and code quality](#testing-and-code-quality)
- [Configuration reference](#configuration-reference)
- [Security notes](#security-notes)
- [Troubleshooting](#troubleshooting)
- [Development roadmap](#development-roadmap)
- [Contributing](#contributing)
- [License](#license)

## Why this project?

Modern supply chains are exposed to uncertain demand, inventory imbalances, transportation delays, equipment failures, and regional disruptions. These events are connected: a vehicle breakdown can delay replenishment, a delayed replenishment can create a stockout, and a stockout can lead to lost sales and reduced service levels.

A useful decision-support system should do more than display static charts. It should connect operational state, forecasting, simulation, and optimization so that different response strategies can be evaluated against a consistent scenario.

This project is intended to provide that environment through a digital-twin-style workflow.

## What the platform is designed to do

### 1. Supply-chain network visibility

Represent the flow of goods across a network of manufacturers, regional warehouses or hubs, retail stores, and delivery vehicles. The dashboard is designed to bring network topology, inventory, fleet activity, and operational indicators into one place.

### 2. Probabilistic demand forecasting

Use LightGBM quantile models to estimate a range of possible demand outcomes rather than presenting only one point estimate:

- **P10:** lower demand estimate
- **P50:** median demand estimate
- **P90:** upper demand estimate

The prediction interval can help decision-makers reason about uncertainty and safety-stock requirements. Forecast quality should be evaluated with appropriate metrics, including pinball loss for quantile predictions.

### 3. Inventory planning and rebalancing

Model replenishment using reorder policies such as `(s, S)`, where `s` is the reorder threshold and `S` is the target stock level. The planned optimization workflow uses Google OR-Tools to evaluate lateral transfers between locations when one warehouse has surplus inventory and another has a shortage.

### 4. Disruption simulation

Introduce operational events such as:

- Vehicle or truck breakdown
- Transportation delay
- Warehouse or facility disruption
- Sudden demand increase
- Inventory shortage

A simulation makes it possible to observe how a local event propagates through the network over time.

### 5. Logistics routing and recovery

The planned routing workflow includes vehicle-capacity constraints, route improvement, and emergency reassignment. A rescue scenario can assign an available vehicle to support a stranded delivery, subject to the constraints represented by the simulation.

### 6. Alerts and recommendations

Surface operational alerts with severity, status, and context. Recommendations are intended to explain the proposed action and its trade-offs. Where approval is required, an authorized user should explicitly approve or reject the recommendation; the backend remains responsible for applying the resulting state change.

### 7. Strategy comparison and experiment analysis

Compare a baseline policy with an intervention under controlled simulation conditions. The planned experiment workflow uses paired random seeds / common random numbers so that the strategies can be compared under comparable simulated conditions. Statistical results must be calculated from the actual experiment output; example values in a demo are not universal performance guarantees.

## End-to-end demonstration workflow

The dashboard is designed around the following narrative. Exact availability of each interaction depends on the current implementation and the data loaded in the running environment.

| Step | Scenario | What to inspect |
| --- | --- | --- |
| A | Healthy network baseline | Network topology, inventory positions, fleet state, and baseline service indicators |
| B | Demand risk | Quantile forecast range and locations/products with elevated demand risk |
| C | Disruption injection | Select or configure an event, such as a delivery-vehicle breakdown |
| D | Operational impact | Advance the simulation and inspect delayed deliveries, inventory pressure, and service impact |
| E | Alert generation | Review alert severity, event context, and the proposed mitigation |
| F | Recovery action | Review and, where supported, approve a recovery recommendation |
| G | Strategy comparison | Compare baseline and intervention results using repeatable simulation runs |
| H | Reset | Restore the scenario to a known starting state for another experiment |

A demonstration may use a small illustrative network (for example, regional hubs, retail stores, and a fleet of delivery vehicles). Any numeric scenario assumptions should be treated as configurable demo inputs, not as real-world operational data.

## System architecture

The application is organized as a frontend, API backend, relational database, and cache / supporting service.

```text
                         User / Browser
                               |
                               v
                    React + TypeScript UI
                         (Nginx / Vite)
                               |
                         HTTP / REST
                               |
                               v
                       FastAPI Backend
                       /      |      \
                      /       |       \
                     v        v        v
              PostgreSQL    Redis   Domain services
              (persistent) (cache)  forecasting /
                                    simulation /
                                    optimization
```

### Frontend

The frontend is a React application written in TypeScript and built with Vite. It is responsible for presenting the operational dashboard, maps, network views, charts, and user interactions. The production container serves the compiled frontend through Nginx and proxies API requests to the backend.

### Backend

The backend is built with FastAPI. It provides the HTTP API, application configuration, authentication and authorization boundaries, database integration, and the service layer where domain workflows are implemented.

The backend uses SQLAlchemy for database access and Alembic for schema migrations. Pydantic Settings centralizes environment-based configuration.

### Data and infrastructure

- **PostgreSQL 16** stores persistent application data.
- **Redis 7** is included as supporting infrastructure for caching and future asynchronous workloads.
- **Docker Compose** coordinates the local multi-service environment.
- **Health checks and service dependencies** help control startup order.

The API health endpoint indicates application/process availability; it should not be interpreted as a complete end-to-end diagnostic of every dependency.

### Simulation and optimization design

The domain design is intended to support a deterministic, discrete-event simulation. A simulation tick can coordinate the clock, disruption events, inbound shipments, demand, replenishment, fulfillment, transfers, vehicle movement, and KPI accounting.

The planned algorithmic components include:

| Area | Intended approach | Purpose |
| --- | --- | --- |
| Simulation | SimPy discrete-event simulation | Advance the supply-chain state in controlled steps |
| Forecasting | LightGBM quantile regression | Estimate demand uncertainty at P10, P50, and P90 |
| Inventory | `(s, S)` replenishment policy | Trigger replenishment when stock reaches a threshold |
| Rebalancing | Google OR-Tools optimization | Evaluate transfers between inventory locations |
| Routing | Capacitated vehicle-routing heuristics and local search | Build and improve feasible delivery routes |
| Emergency response | Nearest-available-vehicle assignment | Support recovery from a vehicle disruption |
| Evaluation | Repeated / paired simulation experiments | Compare policies under controlled random conditions |

These are architectural choices and intended workflows; consult the implementation and tests before assuming that every algorithm is fully integrated or production-ready.

## Technology stack

| Layer | Technologies |
| --- | --- |
| Frontend | React 19, TypeScript, Vite |
| Styling and UI | Tailwind CSS, Lucide React |
| Maps | Leaflet, React Leaflet |
| Network visualization | React Flow |
| Charts | Recharts |
| Backend API | Python 3.12, FastAPI, Uvicorn |
| Validation / configuration | Pydantic Settings |
| Database access | SQLAlchemy, psycopg |
| Migrations | Alembic |
| Database | PostgreSQL 16 |
| Cache / supporting service | Redis 7 |
| Forecasting / numerical computing | LightGBM, NumPy, pandas, SciPy |
| Simulation | SimPy |
| Optimization | Google OR-Tools (planned domain integration) |
| Containers | Docker, Docker Compose |
| Quality checks | Ruff, Black, Mypy, Pytest, TypeScript compiler |

## User roles

The product concept includes role-specific workspaces. The exact permissions and available screens are determined by the backend authorization rules and frontend implementation.

1. **Administrator** — manages the simulation, reviews alerts, and oversees recommendations and experiments.
2. **Distributor** — monitors demand forecasts, inventory across hubs, replenishment, and transfer decisions.
3. **Warehouse Manager** — monitors warehouse stock, capacity, inbound shipments, fulfillment, and dock activity.
4. **Store Owner** — tracks store inventory, availability, incoming deliveries, and shortage risk.
5. **Truck Driver** — views assigned vehicle information, delivery manifests, route details, and relevant disruption notifications.

## Repository structure

The repository is organized into separate application and documentation areas. The main directories include:

```text
.
├── backend/
│   ├── app/                 # FastAPI application and service code
│   ├── migrations/          # Alembic migration environment and revisions
│   ├── scripts/             # Development and data utility scripts
│   ├── tests/               # Backend automated tests
│   ├── Dockerfile
│   └── pyproject.toml       # Python dependencies and tool configuration
├── frontend/
│   ├── src/                 # React / TypeScript application
│   ├── public/              # Static assets
│   ├── Dockerfile
│   └── package.json
├── docs/
│   ├── architecture/        # Architecture decisions and infrastructure notes
│   └── database/            # Database design documentation
├── .github/
│   └── workflows/           # CI workflows
├── docker-compose.yml
├── .env.example
└── README.md
```

Some subdirectories and modules will expand as the simulation, forecasting, and optimization workflows are integrated.

## Getting started

### Prerequisites

Install the following tools:

- Git
- Docker Desktop with Docker Compose v2
- Python 3.12
- Node.js (use a version compatible with the Vite version in the lockfile; Node.js 22 or newer is recommended)
- npm

### 1. Clone the repository

```powershell
git clone https://github.com/agrawalabhi881-a11y/buisyvizzy.git
cd buisyvizzy
```

If you already have the repository locally, switch to the branch you intend to work on and pull its latest changes.

### 2. Create the environment file

From the repository root:

```powershell
Copy-Item .env.example .env
```

Generate two different secrets:

```powershell
$dbPassword = python -c "import secrets; print(secrets.token_urlsafe(24))"
$jwtSecret = python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Open `.env` and replace the example values for `POSTGRES_PASSWORD` and `JWT_SECRET_KEY` with the generated values. Keep the values private and do not commit `.env`.

You can open the file with:

```powershell
notepad .env
```

### 3. Validate and start the services

```powershell
docker compose config
docker compose up --build -d
```

Check service status:

```powershell
docker compose ps
```

Follow logs:

```powershell
docker compose logs -f
```

Follow logs for one service:

```powershell
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
docker compose logs -f redis
```

### 4. Open the application

| Service | Local address | Purpose |
| --- | --- | --- |
| Frontend | http://localhost:3000 | Web dashboard |
| Backend API | http://localhost:8000 | REST API |
| API documentation | http://localhost:8000/docs | Swagger / OpenAPI UI |
| API health | http://localhost:8000/health | Application health check |
| PostgreSQL | localhost:5432 | Database connection from host tools |
| Redis | localhost:6379 | Redis connection from host tools |

The database and Redis ports are for local development. Do not expose them publicly without an explicit security and network configuration.

### 5. Stop the application

```powershell
docker compose down
```

This stops and removes the containers and network while preserving named volumes.

To remove the local database and Redis volumes as well:

```powershell
docker compose down -v
```

**Warning:** `docker compose down -v` deletes persisted local service data. Use it only when you intentionally want a clean environment.

## Running without Docker

Docker Compose is the recommended way to run the complete stack. For isolated backend or frontend development, use separate terminals.

### Backend

From the repository root:

```powershell
Copy-Item backend/.env.example backend/.env
Set-Location backend

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If PowerShell blocks virtual-environment activation, use the Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

A standalone backend needs a valid configuration and a reachable database if the selected application workflow uses PostgreSQL. Configure the required database URL and JWT secret in the backend environment file; do not reuse production secrets for local development.

### Frontend

Open another terminal:

```powershell
Set-Location frontend
npm ci
npm run dev
```

Vite prints the local development URL when the server starts. The production container and development server may use different ports and proxy settings.

## Database migrations

Alembic manages database schema changes.

From the backend directory with the virtual environment active:

```powershell
alembic upgrade head
```

Useful commands:

```powershell
# Show the current database revision
alembic current

# Show migration history
alembic history

# Show the latest available revision
alembic heads

# Generate a migration after changing SQLAlchemy models
alembic revision --autogenerate -m "describe the schema change"
```

Always inspect an autogenerated migration before applying it. Test both upgrade and downgrade behavior where practical. Do not edit an already shared migration in place; create a new revision for subsequent schema changes.

## API overview

The backend exposes REST endpoints under the `/api` prefix. The interactive OpenAPI documentation at `/docs` is the authoritative reference for the routes available in the currently running revision.

The following endpoint groups describe the intended application surface:

| Area | Example endpoint | Purpose |
| --- | --- | --- |
| Simulation state | `GET /api/simulation/state` | Read the current simulation snapshot |
| Simulation control | `POST /api/simulation/tick` | Advance the simulation |
| Simulation reset | `POST /api/simulation/reset` | Reset a scenario to its initial state |
| Disruptions | `POST /api/simulation/disruptions/inject` | Introduce a disruption event |
| Fleet | `GET /api/simulation/fleet` | Read fleet and vehicle information |
| Fleet recovery | `POST /api/simulation/fleet/rescue` | Request a rescue / reassignment action |
| Alerts | `GET /api/alerts` | List operational alerts |
| Alert actions | `POST /api/alerts/{id}/acknowledge` | Acknowledge an alert |
| Recommendations | `GET /api/recommendations` | List mitigation recommendations |
| Recommendation actions | `POST /api/recommendations/{id}/approve` | Approve a recommendation |
| Activity | `GET /api/activity` | Read the activity history |
| Forecasting | `GET /api/forecasting/predict` | Request demand predictions |
| Experiments | `POST /api/simulation/strategy-comparison` | Compare simulation strategies |

Authentication may be required for protected endpoints. Use the login flow and role permissions configured by the application rather than disabling authorization to make a request succeed.

## Testing and code quality

Run backend checks from `backend/`:

```powershell
ruff check .
black --check .
mypy app scripts
pytest
```

Run frontend checks from `frontend/`:

```powershell
npm ci
npx tsc -b --pretty false
npm run build
npm run lint
```

Validate Docker Compose from the repository root:

```powershell
docker compose config
```

Build the service images:

```powershell
docker compose build
```

A successful local command is evidence only for the environment in which it was run. Check the CI status on the pull request as well, and investigate failed or missing workflow runs before merging.

## Configuration reference

The root `.env.example` documents the variables required by Docker Compose. The most important settings are:

| Variable | Purpose |
| --- | --- |
| `POSTGRES_PASSWORD` | Password for the local PostgreSQL service; required |
| `JWT_SECRET_KEY` | Secret used to sign and verify application tokens; required |
| `DATABASE_URL` | Database connection string used by the backend |
| `POSTGRES_PORT` | Host port published for PostgreSQL |
| `REDIS_PORT` | Host port published for Redis |
| `BACKEND_PORT` | Host port published for the API |
| `FRONTEND_PORT` | Host port published for the web application |

Use the exact variable names and defaults documented in the checked-in `.env.example` and Compose file. Never paste real credentials into issues, pull requests, screenshots, or source files.

## Security notes

- Do not commit `.env`, `backend/.env`, private keys, access tokens, or real credentials.
- Use unique, randomly generated secrets for local environments.
- Do not use demo credentials or development settings in a public deployment.
- Keep authentication and role checks enabled for protected operations.
- Validate request data at the API boundary and avoid trusting client-provided role or ownership fields.
- Restrict database and Redis network exposure in any deployment.
- Review dependency updates and third-party licenses before shipping.
- Treat logs and exported simulation data as potentially sensitive if real operational data is introduced.

This repository is an actively developed project, not a security-certified production supply-chain system.

## Troubleshooting

### Docker Compose says a required variable is missing

Check that the root `.env` exists and contains non-empty values for `POSTGRES_PASSWORD` and `JWT_SECRET_KEY`. The example file contains placeholders; copying it alone is not sufficient.

### PostgreSQL reports password authentication failed

The password in the backend connection URL must match the password used to initialize the PostgreSQL volume. If credentials were changed after the volume was created, the database may still retain the old password. Update credentials consistently or, only for disposable local data, recreate the database volume.

### A port is already in use

Stop the process using the port or change the corresponding published port in `.env`. Then re-run:

```powershell
docker compose config
docker compose up -d
```

### A container is unhealthy or exits

Inspect the service logs and status:

```powershell
docker compose ps
docker compose logs --tail 200 backend
docker compose logs --tail 200 postgres
docker compose logs --tail 200 redis
docker compose logs --tail 200 frontend
```

Fix the first underlying error rather than repeatedly restarting all services.

### Frontend cannot reach the API

Confirm that the backend is running and healthy, and that the frontend is using the configured API proxy path. From the host, check the API health URL and inspect the frontend and backend logs.

### Python dependencies or virtual environment behave unexpectedly

Use Python 3.12, recreate the backend virtual environment if it was created with an incompatible interpreter, and install dependencies from `backend/pyproject.toml`.

## Development roadmap

The project is being developed incrementally. The broad workstreams are:

- **Infrastructure and application foundation:** reproducible local services, validated configuration, authentication, migrations, and CI.
- **Core supply-chain domain:** entities and relationships for products, facilities, inventory, shipments, stores, and vehicles.
- **Simulation engine:** deterministic state transitions, event scheduling, disruption handling, and KPI accounting.
- **Forecasting:** data preparation, model training, quantile prediction, and forecast evaluation.
- **Optimization:** replenishment, lateral inventory transfers, vehicle routing, and disruption recovery.
- **Decision support:** alerts, explainable recommendations, role-based workflows, and audit history.
- **Experimentation:** baseline comparisons, repeatable runs, uncertainty reporting, and statistical evaluation.
- **Deployment and observability:** operational logging, metrics, configuration management, and deployment hardening.

The roadmap is directional; use the issues, pull requests, and implementation in the active branch to determine what is complete.

## Contributing

Contributions are welcome. A useful contribution should be focused, tested, and documented.

1. Create a feature branch from the current integration target.
2. Keep changes scoped to one feature or fix.
3. Add or update tests for changed behavior.
4. Run the relevant backend or frontend checks locally.
5. Update documentation when setup, configuration, API behavior, or architecture changes.
6. Open a pull request with a clear summary, implementation notes, and verification results.

Please do not include secrets, generated coverage files, local databases, virtual environments, or build output in commits.

## License

This project is currently an academic and demonstration project. No explicit open-source license is declared here. Review third-party dependency licenses and obtain the necessary permissions before redistribution or commercial use.
