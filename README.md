# NEXUS — Supply Chain Intelligence & Disruption Simulation Platform

> **AI-Powered Supply Chain Digital Twin for Probabilistic Demand Forecasting, Dynamic Disruption Recovery, and Autonomous Logistics Failover.**

---

## 1. Executive Summary & Core Value Proposition

**NEXUS** is an end-to-end, authoritative supply chain intelligence and resilience platform designed to bridge the gap between predictive AI, discrete-event simulation, mathematical optimization, and operational execution:

$$\text{Network Data} \longrightarrow \text{Demand Forecast} \longrightarrow \text{Disruption Shock} \longrightarrow \text{Autonomous Alert} \longrightarrow \text{Trade-off Recommendation} \longrightarrow \text{Truck Rescue / Failover} \longrightarrow \text{Measurable Statistical Outcome}$$

### Key Design Pillars
- **Authoritative Backend Truth:** Single source of truth powered by a deterministic, reproducible SimPy discrete-event simulation engine with zero fabricated frontend metrics.
- **Arrakis Visual Specification:** High-contrast obsidian void theme (`#08090D`), refined typography, luminous accents (Electric Cyan, Signal Amber, Ruby Crimson, Matrix Emerald), monospace metadata counters, and explicit provenance stamps on every metric:
  - `[Backend Authoritative KPI Snapshot]`
  - `[LightGBM Quantile Regressors (P10, P50, P90)]`
  - `[SimPy Discrete-Event Engine (9-Step Canonical Tick)]`
  - `[Common Random Numbers Paired Monte Carlo]`
- **Interactive Geographic Logistics Map:** 20 retail stores, 3 regional hubs (NYC, Chicago, Atlanta), and 10 dynamic fleet vehicles (6–7 moving, 3 parked at warehouse docks).
- **Dynamic Truck Breakdown & Rescue Rerouting:** Live mechanical engine failure simulation on `TRUCK_03` with immediate Haversine nearest-neighbor rescue assignment (`TRUCK_04`) following a 2-segment emergency route:
  $$\text{Rescue Vehicle Origin} \longrightarrow \text{Breakdown Coordinates} \longrightarrow \text{Original Delivery Target Store}$$
- **Guided Demonstration Walkthrough (Stage A → Stage H):** An interactive 8-click tour enabling hackathon judges to step through the complete story from healthy baseline to disruption, autonomous rescue, and statistical validation.

---

## 2. Interactive Guided Demonstration (Stage A → Stage H)

The platform includes a prominent interactive walkthrough at the top of the interface:

| Stage | Title | Description | Primary Screen Action |
| :--- | :--- | :--- | :--- |
| **Stage A** | **Healthy Digital Twin** | 3 hubs, 20 stores, 10 trucks operating at 98.5% OTIF with baseline $(s, S)$ reorder rules. | Inspect digital twin canvas and fleet map. |
| **Stage B** | **Demand Risk Forecast** | LightGBM quantile regression ($P_{10}, P_{50}, P_{90}$) detects $+140\%$ variance demand surge on `PROD_001` at `STORE_04`. | Review probabilistic demand uncertainty fan and pinball loss. |
| **Stage C** | **Inject Disruption Shock** | Trigger sudden powertrain failure on `TRUCK_03` in the Newark/Hackensack corridor (340 perishable units stranded). | Click *"Simulate TRUCK_03 Breakdown"*. |
| **Stage D** | **Observe Shock Impact** | Advance simulation clock (+1 day): fill rate drops, stockout warning fires, lost sales penalty accrues (\$25.00/unit). | Advance simulation tick. |
| **Stage E** | **Autonomous Alert Fired** | Autonomous alert engine triggers `CRITICAL` alert with root-cause diagnostic and cost-benefit trade-off analysis. | Review autonomous mitigation proposal. |
| **Stage F** | **Approve & Execute Rescue** | Click *"Approve Response"*: backend assigns nearest idle truck `TRUCK_04` (Driver Elena Rostova) on emergency transshipment reroute. | Click *"Approve & Execute Response"*. |
| **Stage G** | **Strategy Comparison Lab** | Run paired Monte Carlo experiment ($N=10$ seeds, Common Random Numbers). Student's t-test proves $p < 0.001$ with 95% Confidence Intervals. | Run 10-seed paired simulation. |
| **Stage H** | **Deterministic Reset** | Restore all inventory, fleet positions, and CRN random generators back to Tick 0 for reproducible judging demos. | Reset digital twin. |

---

## 3. System Architecture & Algorithms

### 3.1 Backend Architecture (FastAPI & SimPy)
- **Deterministic Discrete-Event Engine:** SimPy environment executing the canonical 9-step tick loop:
  1. Clock advance & calendar alignment
  2. Disruption trigger & recovery check
  3. Inbound shipment arrival & dock processing
  4. Store customer demand sampling
  5. Store $(s, S)$ replenishment evaluation & order generation
  6. Warehouse order fulfillment & inventory deduction
  7. Distributor lateral transshipment (OR-Tools MILP) & upstream procurement
  8. Truck transit progression & breakdown failover execution
  9. KPI accrual, financial accounting, and snapshot persistence
- **Probabilistic Demand Forecasting:** LightGBM Quantile Regressors trained at quantiles $\alpha \in \{0.10, 0.50, 0.90\}$ directly minimizing pinball loss with lag and rolling features.
- **MILP Lateral Inventory Rebalancing:** Google OR-Tools solver evaluating inter-warehouse transshipments to move surplus stock to deficit hubs before stockouts occur.
- **Capacitated VRP with Dynamic Rerouting:** Clarke-Wright savings heuristic with 2-Opt local search and real-time Haversine nearest-neighbor emergency failover dispatch.

### 3.2 Frontend Architecture (React 19 + TypeScript + Vite + Tailwind CSS)
- **Arrakis Design System:** Void obsidian background (`#08090D`), glassmorphic panels (`backdrop-blur-xl`), razor-thin borders (`border-white/[0.08]`), and luminous semantic status accents.
- **Geographic Logistics Visualizer:** Leaflet map with CartoDB Dark Matter tiles, custom SVG/HTML markers for hubs, stores, moving trucks, broken trucks, and animated gold pulsed rescue routes.
- **Interactive Network Graph:** React Flow canvas displaying supply chain topology (Manufacturer $\to$ Warehouses $\to$ Stores).
- **Time-Series Charts:** Recharts quantile area uncertainty fans, OTIF service level trends, and Monte Carlo recovery trajectories.

---

## 4. 5 Role Personas

Switch personas instantly using the active role selector:

1. **Admin Controller:** Master simulation deck, custom disruption injector, autonomous alerts & recommendations approval, and strategy lab.
2. **Distributor:** Probabilistic demand forecasting deck ($P_{10}, P_{50}, P_{90}$), OR-Tools MILP lateral rebalancing, and upstream $(s, S)$ reorder parameters.
3. **Warehouse Manager:** Strict storage capacity enforcement, lognormal pick-pack lead time queues, shortage escalation, and dock vehicle management.
4. **Store Owner:** 20-store inventory roll-up, on-shelf availability, incoming delivery ETA tracking, and \$25.00/unit unmet demand lost sales penalty logger.
5. **Logistics Truck Driver:** In-cab mobile cockpit, assigned vehicle manifest, GPS waypoint list, and emergency rescue failover alert banner.

---

## 5. Getting Started & Running Locally

### Prerequisites
- Python 3.12+
- Node.js 22+
- Docker Desktop with Docker Compose v2

### Configure the environment

From the repository root, copy the example file and replace its two generated-secret placeholders:

```powershell
Copy-Item .env.example .env
$env:POSTGRES_PASSWORD = python -c "import secrets; print(secrets.token_urlsafe(24))"
$env:JWT_SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(48))"
(Get-Content .env) -replace '^POSTGRES_PASSWORD=.*$', "POSTGRES_PASSWORD=$env:POSTGRES_PASSWORD" | Set-Content .env
(Get-Content .env) -replace '^JWT_SECRET_KEY=.*$', "JWT_SECRET_KEY=$env:JWT_SECRET_KEY" | Set-Content .env
(Get-Content .env) -replace 'replace-with-generated-url-safe-password', $env:POSTGRES_PASSWORD | Set-Content .env
```

The root `.env` is ignored by Git. Do not commit it. For a standalone backend run, you can instead copy `backend/.env.example` to `backend/.env` and set a unique JWT secret.

### Start the full stack

```bash
docker compose up --build
```

- **Frontend Web UI:** `http://localhost:3000` (Nginx with `/api/` reverse proxy)
- **FastAPI Backend:** `http://localhost:8000`
- **PostgreSQL 16:** `localhost:5432`
- **Redis 7:** `localhost:6379`

Stop the stack with `docker compose down`. Persistent data remains in named volumes; `docker compose down -v` deletes those volumes.

### Running manually

```powershell
# Backend (from the repository root)
Copy-Item backend/.env.example backend/.env
Set-Location backend
python -m pip install -e ".[dev]"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Frontend (in another terminal)
Set-Location frontend
npm ci
npm run dev
```

### Test and quality checks

```powershell
# Backend
Set-Location backend
ruff check .
black --check .
mypy app scripts
pytest

# Frontend
Set-Location ../frontend
npm ci
npx tsc -b --pretty false
npm run build
```

---

## 6. Authoritative API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/simulation/state` | Returns the single authoritative backend state (tick, metrics, active disruptions, fleet summary, provenance). |
| `POST` | `/api/simulation/tick` | Advances live discrete-event simulation by 1 tick (day) and logs activity. |
| `POST` | `/api/simulation/reset` | Deterministically resets digital twin engine and alerts back to Tick 0. |
| `POST` | `/api/simulation/truck-breakdown` | Triggers powertrain failure on specified vehicle, emits `CRITICAL` alert, and generates failover rescue recommendation. |
| `POST` | `/api/simulation/fleet/rescue` | Dispatches nearest available rescue vehicle on emergency transshipment reroute. |
| `POST` | `/api/simulation/disruptions/inject` | Schedules custom or preset disruption, generates alert and mitigation recommendation. |
| `GET` | `/api/simulation/fleet` | Returns detailed telemetry, coordinates, and routes for all 10 fleet vehicles. |
| `GET` | `/api/alerts` | Lists operational alerts with optional status and severity query filters. |
| `POST` | `/api/alerts/{id}/acknowledge` | Acknowledges an active operational alert. |
| `POST` | `/api/alerts/{id}/resolve` | Resolves an operational alert. |
| `GET` | `/api/recommendations` | Returns autonomous AI recommendations with trade-off analysis. |
| `POST` | `/api/recommendations/{id}/approve` | Approves and executes recommended intervention in backend simulation engine. |
| `POST` | `/api/recommendations/{id}/reject` | Explicitly declines a recommendation. |
| `GET` | `/api/activity` | Returns audit trail of simulation events, disruptions, and decisions. |
| `GET` | `/api/forecasting/predict` | Computes LightGBM multi-step quantile predictions ($P_{10}, P_{50}, P_{90}$). |
| `POST` | `/api/simulation/strategy-comparison` | Executes paired Monte Carlo experiments ($N=10$ seeds, CRN) with Student's t-test ($p < 0.001$) and 95% confidence intervals. |

---

## 7. License

This project is an academic and demonstration project. Review third-party dependency licenses before redistribution.
