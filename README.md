# AI-Powered Supply Chain Digital Twin

An AI-driven supply chain simulation and decision-support
system for demand forecasting, inventory optimization,
disruption detection, and recovery planning.

## Core Capabilities

- Product-location demand forecasting
- Inventory monitoring and stockout prediction
- Supply chain network simulation
- Inventory redistribution optimization
- Disruption simulation and recovery
- AI-powered supply chain copilot
- Strategy comparison and performance evaluation

## Technology Stack

- Python, FastAPI
- React, Vite
- PostgreSQL, Redis
- LightGBM, Scikit-learn
- Google OR-Tools
- SimPy, NetworkX
- Gemini API, LangGraph
- Docker

## Project Structure

- backend/: API, AI models and simulation
- frontend/: Web dashboard
- data/: Historical and synthetic data
- docs/: Architecture and documentation
- infra/: Deployment configuration

## Project Status

Phase 2 - Supply-chain data model and initial database schema.

The development catalog contains exactly 10 original M5 stores and 50 original M5 products. The manufacturer, distributors, warehouses, trucks, drivers and assignments are assumed project infrastructure; no synthetic stores, products or inventory quantities are seeded. Store display labels are `Store 1` through `Store 10`, while original `store_id` values remain unchanged. See [the entity relationship diagram](docs/database/erd.md) and [data dictionary](docs/database/data-dictionary.md). Apply the schema with Alembic, then run `python -m scripts.seed` and `python -m app.ingestion.m5` from `backend/` after setting `DATABASE_URL` and placing the M5 files under `data/raw/m5/`.

For Phase 3 ingestion instructions and the default 50-product M5 sample, see [M5 ingestion](docs/data/m5_ingestion.md).
