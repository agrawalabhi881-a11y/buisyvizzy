"""
backend/tests/test_forecasting.py
Unit and integration tests for Phase 6: Probabilistic Quantile Demand Forecasting.
Tests feature engineering, LightGBM quantile regression (P10, P50, P90),
monotonicity constraints, pinball loss evaluation, and FastAPI endpoints.
"""

import sys
import os
import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

try:
    from app.main import app
    from app.forecasting.feature_engineering import DemandFeatureEngineer
    from app.forecasting.quantile_model import LightGBMQuantileForecaster
    from app.services.forecasting_service import ForecastingService
    from app.services.auth_service import create_access_token
except ImportError:
    from backend.app.main import app
    from backend.app.forecasting.feature_engineering import DemandFeatureEngineer
    from backend.app.forecasting.quantile_model import LightGBMQuantileForecaster
    from backend.app.services.forecasting_service import ForecastingService
    from backend.app.services.auth_service import create_access_token


client = TestClient(app)


def test_feature_engineering_lags_and_rolling():
    """Validates calendar indicators, lags, and rolling stats without NaN leakage."""
    dates = pd.date_range("2025-01-01", periods=45)
    records = []
    for d in dates:
        records.append({
            "store_id": "STORE_01",
            "product_id": "PROD_001",
            "date": d.strftime("%Y-%m-%d"),
            "sales": float(d.day % 10 + 5),
        })
    df = pd.DataFrame(records)
    feat_df = DemandFeatureEngineer.extract_features(df)

    # Check calendar features
    assert "day_of_week" in feat_df.columns
    assert "is_weekend" in feat_df.columns
    assert "month" in feat_df.columns

    # Check lag features
    for lag in [1, 7, 14, 28]:
        assert f"sales_lag_{lag}" in feat_df.columns

    # Check rolling features
    for win in [7, 14, 28]:
        assert f"rolling_mean_{win}" in feat_df.columns
        assert f"rolling_std_{win}" in feat_df.columns

    # Ensure no NaN values remain
    assert feat_df.isna().sum().sum() == 0


def test_time_based_split_no_leakage():
    """Ensures chronological split has strictly separated dates."""
    dates = pd.date_range("2025-01-01", periods=30)
    df = pd.DataFrame({
        "store_id": "S1",
        "product_id": "P1",
        "date": dates,
        "sales": 10.0,
    })
    split_date = "2025-01-20"
    train_df, val_df = DemandFeatureEngineer.time_based_split(df, split_date)

    assert train_df["date"].max() < pd.to_datetime(split_date)
    assert val_df["date"].min() >= pd.to_datetime(split_date)
    assert len(train_df) + len(val_df) == len(df)


def test_quantile_forecaster_monotonicity_and_coverage():
    """Tests that LightGBM quantile model satisfies P10 <= P50 <= P90 and pinball loss is positive."""
    service = ForecastingService()
    raw_df = service.generate_training_dataset(days=70, n_stores=2, n_products=3)
    feat_df = DemandFeatureEngineer.extract_features(raw_df)

    split_date = feat_df["date"].quantile(0.80).strftime("%Y-%m-%d")
    train_df, val_df = DemandFeatureEngineer.time_based_split(feat_df, split_date)

    forecaster = LightGBMQuantileForecaster(n_estimators=30, learning_rate=0.1, seed=42)
    forecaster.fit(train_df)
    preds = forecaster.predict_quantiles(val_df)

    # Monotonicity check: P10 <= P50 <= P90
    assert (preds["pred_p10"] <= preds["pred_p50"] + 1e-5).all(), "P10 must be <= P50"
    assert (preds["pred_p50"] <= preds["pred_p90"] + 1e-5).all(), "P50 must be <= P90"
    assert (preds["pred_p10"] >= 0.0).all(), "Predictions must be non-negative"

    metrics = forecaster.evaluate(val_df)
    assert metrics.pinball_loss_p10 > 0.0
    assert metrics.pinball_loss_p50 > 0.0
    assert metrics.pinball_loss_p90 > 0.0
    assert metrics.average_pinball_loss > 0.0
    # Empirical coverage of 80% nominal interval should be reasonable
    assert 50.0 <= metrics.empirical_coverage_80 <= 100.0


def test_forecasting_service_horizon():
    """Tests multi-step horizon prediction output contracts."""
    service = ForecastingService()
    # Fast training with smaller dataset
    fast_df = service.generate_training_dataset(days=50, n_stores=2, n_products=2)
    service.train_and_evaluate(fast_df)

    contracts = service.predict_horizon(store_id="STORE_01", product_id="PROD_001", horizon_days=7, current_tick=10)
    assert len(contracts) == 7
    for i, c in enumerate(contracts):
        assert c.store_id == "STORE_01"
        assert c.product_id == "PROD_001"
        assert c.tick == 10 + i
        assert c.p10 <= c.p50 <= c.p90


def test_forecasting_api_endpoints():
    """Tests FastAPI /api/forecasting/train and /api/forecasting/predict endpoints with RBAC."""
    admin_token = create_access_token({"sub": "admin1", "role": "ADMIN"})
    driver_token = create_access_token({"sub": "driver1", "role": "TRUCK_DRIVER"})

    # 1. Driver should be forbidden from training
    res_forbidden = client.post(
        "/api/forecasting/train",
        headers={"Authorization": f"Bearer {driver_token}"},
    )
    assert res_forbidden.status_code == 403

    # 2. Admin can trigger training
    res_train = client.post(
        "/api/forecasting/train",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_train.status_code == 200
    data = res_train.json()
    assert data["status"] == "trained"
    assert "metrics" in data
    assert "empirical_coverage_80" in data["metrics"]

    # 3. Predict horizon
    res_pred = client.get(
        "/api/forecasting/predict?store_id=STORE_01&product_id=PROD_001&horizon_days=5",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_pred.status_code == 200
    pred_data = res_pred.json()
    assert len(pred_data) == 5
    assert pred_data[0]["p10"] <= pred_data[0]["p50"] <= pred_data[0]["p90"]
