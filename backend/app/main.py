from fastapi import FastAPI

from app.api.routes.health import router as health_router

app = FastAPI(title="Supply Chain Digital Twin API")
app.include_router(health_router)


@app.get("/", tags=["service"])
def root() -> dict[str, str]:
    return {"service": "supply-chain-digital-twin", "status": "ok"}
