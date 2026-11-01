"""
backend/app/sim/demand.py
Stochastic & historical demand generation for stores and products.
Supports Poisson/Neg-Binomial with day-of-week seasonality, historical replay,
and quantile-based stochastic sampling.
"""

from typing import Dict, List, Optional
import numpy as np


class DemandGenerator:
    """Generates customer demand per store and product per simulation tick."""

    def __init__(self, rng: Optional[np.random.Generator] = None, seed: int = 42):
        self.rng = rng or np.random.default_rng(seed)
        # Baseline demand mean per product category (units/day)
        self.category_base_mean: Dict[str, float] = {
            "Beverages": 18.0,
            "Snacks": 14.0,
            "Household": 8.0,
            "Personal Care": 6.0,
            "Dairy": 15.0,
        }
        # Day of week multiplier (assuming tick % 7: 0=Mon, 5=Sat, 6=Sun)
        self.dow_multipliers = [0.85, 0.90, 0.92, 0.95, 1.15, 1.35, 1.25]
        # Replay cache: (store_id, product_id, tick) -> float
        self.history_cache: Dict[tuple, float] = {}

    def set_historical_data(self, history: Dict[tuple, float]):
        """Sets pre-loaded historical sales data for replay mode."""
        self.history_cache = history

    def sample_demand(
        self,
        store_id: str,
        product_id: str,
        category: str,
        tick: int,
        disruption_multiplier: float = 1.0,
        forecast_quantiles: Optional[tuple] = None,
    ) -> float:
        """
        Samples consumer demand at a store for a product on tick t.
        Priority:
          1. Historical replay if in cache.
          2. Forecast quantiles (P10, P50, P90) sampling if provided.
          3. Stochastic Poisson/Normal with Day-of-Week seasonality.
        """
        key = (store_id, product_id, tick)
        if key in self.history_cache:
            raw_val = self.history_cache[key]
            return float(max(0.0, raw_val * disruption_multiplier))

        if forecast_quantiles is not None:
            # Triangular distribution parameterized by (P10, P50, P90)
            p10, p50, p90 = forecast_quantiles
            sampled = self.rng.triangular(left=max(0.0, p10), mode=max(0.0, p50), right=max(p50, p90))
            return float(max(0.0, round(sampled * disruption_multiplier, 1)))

        # Default: Parametric model
        base_lambda = self.category_base_mean.get(category, 10.0)
        dow_factor = self.dow_multipliers[tick % 7]
        effective_lambda = base_lambda * dow_factor * disruption_multiplier

        # Use Poisson for discrete demand arrivals
        sampled_demand = float(self.rng.poisson(lam=effective_lambda))
        return sampled_demand
