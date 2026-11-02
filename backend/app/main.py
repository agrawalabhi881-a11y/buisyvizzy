from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.warehouses import router as warehouses_router
from app.api.routes.stores import router as stores_router
from app.api.routes.procurement import router as procurement_router
from app.api.routes.simulation import router as simulation_router
from app.api.routes.forecasting import router as forecasting_router
from app.api.routes.alerts import router as alerts_router
from app.api.routes.contract_aliases import router as contract_aliases_router
from app.api.routes.web import router as web_router

app = FastAPI(
    title="NEXUS — Supply Chain Digital Twin API",
    description="Simulation-based decision-support system with demand forecasting, disruption recovery, MILP rebalancing, and dynamic fleet failover.",
    version="2.0.0",
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routers with and without /api prefix for maximum client flexibility
app.include_router(health_router)
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(warehouses_router, prefix="/api")
app.include_router(stores_router, prefix="/api")
app.include_router(procurement_router, prefix="/api")
app.include_router(simulation_router, prefix="/api")
app.include_router(forecasting_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")
app.include_router(contract_aliases_router, prefix="/api")
app.include_router(contract_aliases_router)
app.include_router(web_router)


@app.get("/", tags=["service"])
def root() -> dict[str, str]:
    return {"service": "supply-chain-digital-twin", "status": "ok"}
