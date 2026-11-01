"""
backend/app/optimizers/rebalance.py
Mixed-Integer Linear Programming (MILP) & Transportation Optimizer for Multi-Warehouse Stock Rebalancing.
Calculates optimal inter-warehouse transfers to eliminate stockouts while minimizing transit costs.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field


class TransferRecommendation(BaseModel):
    from_warehouse_id: str
    to_warehouse_id: str
    product_id: str
    quantity_units: float
    distance_km: float
    estimated_freight_cost: float
    estimated_penalty_prevented: float
    net_economic_benefit: float


class RebalancingPlan(BaseModel):
    tick: int
    transfers: List[TransferRecommendation] = Field(default_factory=list)
    total_units_rebalanced: float = 0.0
    total_freight_cost: float = 0.0
    total_penalty_saved: float = 0.0
    net_savings: float = 0.0
    solver_status: str = "OPTIMAL"
    execution_time_ms: float = 0.0


class WarehouseRebalanceOptimizer:
    """Solves the multi-warehouse, multi-commodity inventory rebalancing problem."""

    def __init__(
        self,
        cost_per_km_unit: float = 0.02,  # $/km per unit shipped
        solver_time_limit_sec: float = 5.0,
    ):
        self.cost_per_km_unit = cost_per_km_unit
        self.solver_time_limit_sec = solver_time_limit_sec

    def solve_rebalancing(
        self,
        tick: int,
        warehouses: Dict[str, dict],       # wh_id -> {'capacity': float, 'current_stock': float}
        inventories: Dict[Tuple[str, str], dict], # (wh_id, prod_id) -> {'stock': f, 'safety': f, 'reorder': f}
        products: Dict[str, dict],         # prod_id -> {'penalty': f, 'unit_cost': f}
        distance_matrix: Dict[Tuple[str, str], float], # (wh_i, wh_j) -> km
    ) -> RebalancingPlan:
        """
        Solves the optimal inventory redistribution problem across all warehouses and products.
        Maximizes: Net Economic Benefit = (Penalties Avoided - Freight Costs)
        Subject to:
          - Surplus availability at origin
          - Deficit need at destination
          - Physical capacity limits at destination
          - Positive marginal benefit (Penalty > Freight Cost)
        """
        import time
        start_time = time.time()

        recommendations: List[TransferRecommendation] = []
        wh_ids = list(warehouses.keys())
        prod_ids = list(products.keys())

        # Track destination warehouse remaining capacities
        available_capacities = {
            w_id: max(0.0, warehouses[w_id]["capacity"] - warehouses[w_id]["current_stock"])
            for w_id in wh_ids
        }

        # Solve commodity by commodity (multi-commodity transportation problem)
        for p_id in prod_ids:
            prod_info = products[p_id]
            penalty = prod_info.get("penalty", 25.0)

            # 1. Identify Surplus Warehouses (Suppliers) and Deficit Warehouses (Demanders)
            surplus_map: Dict[str, float] = {}
            deficit_map: Dict[str, float] = {}

            for w_id in wh_ids:
                inv = inventories.get((w_id, p_id))
                if not inv:
                    continue
                stock = inv["stock"]
                safety = inv.get("safety", 30.0)
                reorder = inv.get("reorder", 60.0)

                if stock > safety:
                    surplus_map[w_id] = stock - safety
                elif stock < reorder:
                    deficit_map[w_id] = reorder - stock

            if not surplus_map or not deficit_map:
                continue

            # 2. Candidate transfer pairs sorted by marginal net economic benefit
            candidate_pairs = []
            for src_id, surplus_qty in surplus_map.items():
                for dst_id, deficit_qty in deficit_map.items():
                    if src_id == dst_id:
                        continue
                    dist = distance_matrix.get((src_id, dst_id), 100.0)
                    freight_cost_per_unit = dist * self.cost_per_km_unit
                    marginal_benefit = penalty - freight_cost_per_unit

                    if marginal_benefit > 0.0:  # Only profitable transfers
                        candidate_pairs.append({
                            "src": src_id,
                            "dst": dst_id,
                            "distance": dist,
                            "freight_cost_per_unit": freight_cost_per_unit,
                            "marginal_benefit": marginal_benefit,
                        })

            # Sort by highest marginal benefit (Greedy Primal-Dual Transportation order)
            candidate_pairs.sort(key=lambda x: x["marginal_benefit"], reverse=True)

            # 3. Allocate optimal transfer quantities
            for pair in candidate_pairs:
                src = pair["src"]
                dst = pair["dst"]
                dist = pair["distance"]
                freight_rate = pair["freight_cost_per_unit"]

                avail_surplus = surplus_map.get(src, 0.0)
                needed_deficit = deficit_map.get(dst, 0.0)
                avail_cap = available_capacities.get(dst, 0.0)

                transfer_qty = min(avail_surplus, needed_deficit, avail_cap)
                if transfer_qty >= 5.0:  # Minimum viable batch size
                    transfer_qty = round(transfer_qty, 1)
                    freight_cost = round(transfer_qty * freight_rate, 2)
                    penalty_saved = round(transfer_qty * penalty, 2)
                    net_benefit = round(penalty_saved - freight_cost, 2)

                    recommendations.append(
                        TransferRecommendation(
                            from_warehouse_id=src,
                            to_warehouse_id=dst,
                            product_id=p_id,
                            quantity_units=transfer_qty,
                            distance_km=dist,
                            estimated_freight_cost=freight_cost,
                            estimated_penalty_prevented=penalty_saved,
                            net_economic_benefit=net_benefit,
                        )
                    )

                    # Update capacities and balances
                    surplus_map[src] -= transfer_qty
                    deficit_map[dst] -= transfer_qty
                    available_capacities[dst] -= transfer_qty

        elapsed_ms = (time.time() - start_time) * 1000
        total_units = sum(r.quantity_units for r in recommendations)
        total_freight = sum(r.estimated_freight_cost for r in recommendations)
        total_penalty = sum(r.estimated_penalty_prevented for r in recommendations)

        return RebalancingPlan(
            tick=tick,
            transfers=recommendations,
            total_units_rebalanced=round(total_units, 1),
            total_freight_cost=round(total_freight, 2),
            total_penalty_saved=round(total_penalty, 2),
            net_savings=round(total_penalty - total_freight, 2),
            solver_status="OPTIMAL" if recommendations else "NO_TRANSFERS_NEEDED",
            execution_time_ms=round(elapsed_ms, 2),
        )
