"""
backend/app/forecasting/quantile_model.py
LightGBM Quantile Regressors for Probabilistic Demand Forecasting (P10, P50, P90).
Evaluates with Pinball Loss, calculates empirical 80% coverage, and compares against Seasonal Naive baseline.
"""

from typing import Dict, List, Optional, Tuple
import lightgbm as lgb
import numpy as np
import pandas as pd
from pydantic import BaseModel


class QuantileForecastMetrics(BaseModel):
    pinball_loss_p10: float
    pinball_loss_p50: float
    pinball_loss_p90: float
    average_pinball_loss: float
    empirical_coverage_80: float
    baseline_mae: float
    model_mae: float
    mae_improvement_pct: float


class LightGBMQuantileForecaster:
    """Trains and predicts quantile demand models for P10, P50, P90."""

    QUANTILES = [0.10, 0.50, 0.90]
    FEATURE_COLS = [
        "day_of_week",
        "day_of_month",
        "month",
        "is_weekend",
        "sales_lag_1",
        "sales_lag_7",
        "sales_lag_14",
        "sales_lag_28",
        "rolling_mean_7",
        "rolling_mean_14",
        "rolling_mean_28",
        "rolling_std_7",
    ]

    def __init__(self, n_estimators: int = 100, learning_rate: float = 0.05, seed: int = 42):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.seed = seed
        # Models per quantile: alpha -> lgb.LGBMRegressor
        self.models: Dict[float, lgb.LGBMRegressor] = {}

    def fit(self, train_df: pd.DataFrame, target_col: str = "sales"):
        """Trains 3 distinct LightGBM quantile regression models."""
        X_train = train_df[self.FEATURE_COLS]
        y_train = train_df[target_col]

        for q in self.QUANTILES:
            model = lgb.LGBMRegressor(
                objective="quantile",
                alpha=q,
                n_estimators=self.n_estimators,
                learning_rate=self.learning_rate,
                random_state=self.seed,
                verbose=-1,
                min_child_samples=5,
            )
            model.fit(X_train, y_train)
            self.models[q] = model

    def predict_quantiles(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Outputs DataFrame with columns: ['pred_p10', 'pred_p50', 'pred_p90']
        Ensures non-negative outputs and quantile monotonicity: P10 <= P50 <= P90.
        """
        X = df[self.FEATURE_COLS]
        preds = {}
        for q in self.QUANTILES:
            col_name = f"pred_p{int(q*100)}"
            preds[col_name] = np.maximum(0.0, self.models[q].predict(X))

        res_df = pd.DataFrame(preds, index=df.index)
        # Enforce quantile monotonicity
        res_df["pred_p50"] = np.maximum(res_df["pred_p10"], res_df["pred_p50"])
        res_df["pred_p90"] = np.maximum(res_df["pred_p50"], res_df["pred_p90"])
        return res_df

    @staticmethod
    def pinball_loss(y_true: np.ndarray, y_pred: np.ndarray, alpha: float) -> float:
        """Computes asymmetric quantile loss."""
        diff = y_true - y_pred
        return float(np.mean(np.maximum(alpha * diff, (alpha - 1.0) * diff)))

    def evaluate(self, val_df: pd.DataFrame, target_col: str = "sales") -> QuantileForecastMetrics:
        """
        Evaluates predictions against true validation targets:
        - Pinball losses at P10, P50, P90
        - Empirical coverage [P10, P90]
        - MAE improvement over Seasonal-Naive baseline (7-day lag)
        """
        y_true = val_df[target_col].values
        preds_df = self.predict_quantiles(val_df)

        p10 = preds_df["pred_p10"].values
        p50 = preds_df["pred_p50"].values
        p90 = preds_df["pred_p90"].values

        loss_10 = self.pinball_loss(y_true, p10, 0.10)
        loss_50 = self.pinball_loss(y_true, p50, 0.50)
        loss_90 = self.pinball_loss(y_true, p90, 0.90)
        avg_loss = (loss_10 + loss_50 + loss_90) / 3.0

        # Empirical Coverage: fraction of actuals inside [P10, P90]
        covered = np.logical_and(y_true >= p10, y_true <= p90)
        coverage_pct = float(np.mean(covered) * 100.0)

        # Baseline: Seasonal Naive (7-day lag persistence)
        baseline_preds = val_df["sales_lag_7"].values if "sales_lag_7" in val_df else np.roll(y_true, 7)
        baseline_mae = float(np.mean(np.abs(y_true - baseline_preds)))
        model_mae = float(np.mean(np.abs(y_true - p50)))

        improvement = ((baseline_mae - model_mae) / baseline_mae * 100.0) if baseline_mae > 0 else 0.0

        return QuantileForecastMetrics(
            pinball_loss_p10=round(loss_10, 4),
            pinball_loss_p50=round(loss_50, 4),
            pinball_loss_p90=round(loss_90, 4),
            average_pinball_loss=round(avg_loss, 4),
            empirical_coverage_80=round(coverage_pct, 2),
            baseline_mae=round(baseline_mae, 2),
            model_mae=round(model_mae, 2),
            mae_improvement_pct=round(improvement, 2),
        )
