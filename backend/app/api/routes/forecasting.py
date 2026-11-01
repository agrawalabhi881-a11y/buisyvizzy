"""
backend/app/api/routes/forecasting.py
Probabilistic demand forecasting endpoints:
LightGBM training, Pinball Loss evaluation, and Quantile (P10, P50, P90) predictions.
"""

from typing import List, Optional
from fastapi import APIRouter, Security
from pydantic import BaseModel

from app.services.auth_service import UserProfile, require_roles
from app.services.forecasting_service import ForecastingService
from app.contracts.models import ForecastContract

router = APIRouter(prefix="/forecasting", tags=["Forecasting"])
forecast_service_instance = ForecastingService()


@router.post("/train")
def train_forecasting_model(
    user: UserProfile = Security(require_roles(["ADMIN", "DISTRIBUTOR"])),
):
    """
    Trains LightGBM Quantile Regressors (P10, P50, P90) with lag & rolling features.
    Evaluates Pinball Loss, Empirical Coverage (~80%), and compares against Seasonal Naive baseline.
    """
    metrics = forecast_service_instance.train_and_evaluate()
    return {
        "status": "trained",
        "model": "LightGBM Quantile Regressor",
        "quantiles": [0.10, 0.50, 0.90],
        "metrics": metrics.model_dump(),
    }


@router.get("/predict", response_model=List[ForecastContract])
def predict_quantiles(
    store_id: str = "STORE_01",
    product_id: str = "PROD_001",
    horizon_days: int = 7,
    current_tick: int = 0,
    user: UserProfile = Security(require_roles(["ADMIN", "DISTRIBUTOR", "STORE_OWNER"])),
):
    """
    Generates multi-step probabilistic demand predictions (P10, P50, P90) for a given store and product.
    """
    return forecast_service_instance.predict_horizon(
        store_id=store_id,
        product_id=product_id,
        horizon_days=horizon_days,
        current_tick=current_tick,
    )
