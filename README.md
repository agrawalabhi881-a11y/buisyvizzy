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

The reproducible seed network contains 1 manufacturer, 2 distributors, 3 warehouses, 10 stores, 50 products, 10 trucks and 10 drivers. Stores and products without a supplied catalog are explicitly synthetic and do not receive fabricated M5 identifiers. See [the entity relationship diagram](docs/database/erd.md) and [data dictionary](docs/database/data-dictionary.md). Apply the schema with Alembic, then seed with `python -m scripts.seed` from `backend/` after setting `DATABASE_URL`. To map real M5 identifiers later, pass a JSON catalog path using `--catalog`; the JSON accepts `stores` (`store_id`, `state_id`, optional `name`) and `products` (`item_id`, `dept_id`, `cat_id`, optional `name`) arrays. See `backend/scripts/m5_catalog.example.json`.
