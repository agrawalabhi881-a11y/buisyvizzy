"""
backend/app/forecasting/feature_engineering.py
Time-series feature engineering pipeline for LightGBM quantile demand forecasting.
Extracts calendar indicators, lag variables, and rolling statistics on historical sales.
Strict time-based train/validation split (no data leakage).
"""

from typing import Tuple, List, Optional
import numpy as np
import pandas as pd


class DemandFeatureEngineer:
    """Transforms raw product-store daily sales histories into feature matrices."""

    LAG_DAYS = [1, 7, 14, 28]
    ROLLING_WINDOWS = [7, 14, 28]

    @staticmethod
    def extract_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Expects df with columns: ['store_id', 'product_id', 'date', 'sales']
        Calculates time-series lags, rolling means, and calendar signals per (store, product).
        """
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values(["store_id", "product_id", "date"]).reset_index(drop=True)

        # 1. Calendar Features
        df["day_of_week"] = df["date"].dt.dayofweek
        df["day_of_month"] = df["date"].dt.day
        df["month"] = df["date"].dt.month
        df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

        # 2. Lag Features per (store, product)
        for lag in DemandFeatureEngineer.LAG_DAYS:
            df[f"sales_lag_{lag}"] = df.groupby(["store_id", "product_id"])["sales"].shift(lag)

        # 3. Rolling Statistics (computed on lag_1 to avoid target leakage)
        for window in DemandFeatureEngineer.ROLLING_WINDOWS:
            df[f"rolling_mean_{window}"] = (
                df.groupby(["store_id", "product_id"])["sales_lag_1"]
                .transform(lambda s: s.rolling(window, min_periods=3).mean())
            )
            df[f"rolling_std_{window}"] = (
                df.groupby(["store_id", "product_id"])["sales_lag_1"]
                .transform(lambda s: s.rolling(window, min_periods=3).std())
            )

        # Forward fill and fillna with 0 for earliest warmup periods
        df = df.bfill().fillna(0.0)
        return df

    @staticmethod
    def time_based_split(
        df: pd.DataFrame,
        split_date: str,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Splits data chronologically on split_date.
        Never use random K-Fold splits on time-series data to prevent future leakage.
        """
        df["date"] = pd.to_datetime(df["date"])
        train_df = df[df["date"] < pd.to_datetime(split_date)].copy()
        val_df = df[df["date"] >= pd.to_datetime(split_date)].copy()
        return train_df, val_df
