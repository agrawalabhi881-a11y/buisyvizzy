"""
backend/app/services/forecasting_service.py
Forecasting domain service:
Manages probabilistic demand forecasting, feature engineering, and model training.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from app.forecasting.feature_engineering import DemandFeatureEngineer
from app.forecasting.quantile_model import LightGBMQuantileForecaster, QuantileForecastMetrics
from app.contracts.models import ForecastContract


class ForecastingService:
    """Manages ML training, evaluation, and inference of quantile demand predictions."""

    def __init__(self):
        self.forecaster = LightGBMQuantileForecaster(n_estimators=80, learning_rate=0.08)
        self.is_trained: bool = False
        self.last_metrics: Optional[QuantileForecastMetrics] = None
        self.history_df: Optional[pd.DataFrame] = None

    @staticmethod
    def generate_training_dataset(days: int = 120, n_stores: int = 5, n_products: int = 10) -> pd.DataFrame:
        """Generates realistic synthetic historical demand dataset with seasonality and trend."""
        rng = np.random.default_rng(42)
        records = []
        base_date = datetime(2025, 1, 1)

        dow_factors = [0.85, 0.90, 0.92, 0.95, 1.15, 1.35, 1.25]  # Weekend peaks

        for s_idx in range(1, n_stores + 1):
            s_id = f"STORE_{s_idx:02d}"
            store_mult = 0.8 + (s_idx * 0.1)

            for p_idx in range(1, n_products + 1):
                p_id = f"PROD_{p_idx:03d}"
                base_demand = 8.0 + (p_idx % 5) * 3.0

                for d in range(days):
                    dt = base_date + timedelta(days=d)
                    dow = dt.weekday()
                    mean_val = base_demand * store_mult * dow_factors[dow]
                    # Poisson demand with random noise
                    sales = max(0.0, float(rng.poisson(mean_val)))

                    records.append({
                        "store_id": s_id,
                        "product_id": p_id,
                        "date": dt.strftime("%Y-%m-%d"),
                        "sales": sales,
                    })

        return pd.DataFrame(records)

    def train_and_evaluate(self, df: Optional[pd.DataFrame] = None) -> QuantileForecastMetrics:
        """Builds features, splits chronologically, trains LightGBM models, and returns metrics."""
        raw_df = df if df is not None else self.generate_training_dataset(days=120)
        self.history_df = raw_df
        feat_df = DemandFeatureEngineer.extract_features(raw_df)

        # 80/20 Chronological train/val split (split at day 96)
        split_date = feat_df["date"].quantile(0.80).strftime("%Y-%m-%d")
        train_df, val_df = DemandFeatureEngineer.time_based_split(feat_df, split_date)

        self.forecaster.fit(train_df)
        self.is_trained = True
        self.last_metrics = self.forecaster.evaluate(val_df)
        return self.last_metrics

    def predict_horizon(
        self,
        store_id: str,
        product_id: str,
        horizon_days: int = 7,
        current_tick: int = 0,
        history: Optional[pd.DataFrame] = None,
    ) -> List[ForecastContract]:
        """Generates multi-step probabilistic quantile forecast (P10, P50, P90)."""
        if not self.is_trained:
            self.train_and_evaluate()

        # Gather preceding history for accurate lags and rolling windows
        hist_source = history if history is not None else self.history_df
        if hist_source is not None:
            hist_match = hist_source[
                (hist_source["store_id"] == store_id) & (hist_source["product_id"] == product_id)
            ].sort_values("date").tail(35)
        else:
            hist_match = pd.DataFrame()

        # Fallback baseline history if none exists for this specific combination
        if hist_match.empty:
            warmup_records = []
            base_date = datetime(2025, 4, 1) + timedelta(days=current_tick - 35)
            for d in range(35):
                dt = base_date + timedelta(days=d)
                warmup_records.append({
                    "store_id": store_id,
                    "product_id": product_id,
                    "date": dt.strftime("%Y-%m-%d"),
                    "sales": 10.0 + (d % 7),
                })
            hist_match = pd.DataFrame(warmup_records)

        # Generate future placeholder rows
        last_date = pd.to_datetime(hist_match["date"].max())
        future_rows = []
        for h in range(1, horizon_days + 1):
            dt = last_date + timedelta(days=h)
            future_rows.append({
                "store_id": store_id,
                "product_id": product_id,
                "date": dt.strftime("%Y-%m-%d"),
                "sales": 0.0,  # Placeholder for future
            })

        combined_df = pd.concat([hist_match, pd.DataFrame(future_rows)], ignore_index=True)
        feat_df = DemandFeatureEngineer.extract_features(combined_df)
        future_feat = feat_df.tail(horizon_days).reset_index(drop=True)
        preds_df = self.forecaster.predict_quantiles(future_feat)

        results = []
        for i, row in preds_df.iterrows():
            results.append(
                ForecastContract(
                    store_id=store_id,
                    product_id=product_id,
                    tick=current_tick + i,
                    p10=round(float(row["pred_p10"]), 1),
                    p50=round(float(row["pred_p50"]), 1),
                    p90=round(float(row["pred_p90"]), 1),
                )
            )
        return results
