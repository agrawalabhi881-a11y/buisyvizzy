"""
backend/app/optimizers/vrp.py
Capacitated Vehicle Routing Problem (CVRP) Optimizer with 2-Opt Route Untangling.
Calculates optimal multi-stop truck routes departing from warehouses to stores within each cluster.
"""

from typing import Dict, List, Optional, Tuple
import math
import numpy as np
from pydantic import BaseModel, Field


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance in kilometers."""
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(r * c, 2)


class VRPStop(BaseModel):
    store_id: str
    lat: float
    lon: float
    demand_units: float
    arrival_order: int
    distance_from_prev_km: float


class VRPRoute(BaseModel):
    truck_id: str
    warehouse_id: str
    stops: List[VRPStop] = Field(default_factory=list)
    total_cargo_units: float = 0.0
    total_distance_km: float = 0.0
    estimated_fuel_cost: float = 0.0
    driver_salary_share: float = 0.0
    estimated_transit_hours: float = 0.0


class VRPDispatchPlan(BaseModel):
    cluster_id: int
    warehouse_id: str
    routes: List[VRPRoute] = Field(default_factory=list)
    total_distance_km: float = 0.0
    total_cargo_delivered: float = 0.0
    unassigned_stores: List[str] = Field(default_factory=list)
    execution_time_ms: float = 0.0


class CVRPOptimizer:
    """
    Solves Capacitated Vehicle Routing using Clarke-Wright Savings
    coupled with 2-Opt local search post-optimization.
    """

    def __init__(self, speed_km_h: float = 55.0, fuel_cost_per_km: float = 1.25):
        self.speed_km_h = speed_km_h
        self.fuel_cost_per_km = fuel_cost_per_km

    def solve_cluster_vrp(
        self,
        cluster_id: int,
        warehouse_id: str,
        wh_coord: Tuple[float, float],           # (lat, lon)
        store_demands: Dict[str, float],         # store_id -> cargo_units
        store_coords: Dict[str, Tuple[float, float]], # store_id -> (lat, lon)
        available_trucks: List[dict],            # list of {'id': str, 'capacity': float, 'driver_salary': float}
    ) -> VRPDispatchPlan:
        """
        Calculates optimal multi-stop delivery routes departing from warehouse_id.
        """
        import time
        t0 = time.time()

        active_stores = [s for s, d in store_demands.items() if d > 0]
        if not active_stores or not available_trucks:
            return VRPDispatchPlan(
                cluster_id=cluster_id,
                warehouse_id=warehouse_id,
                routes=[],
                unassigned_stores=active_stores,
            )

        # 1. Compute Distance Matrix (0 is depot / warehouse)
        node_ids = ["DEPOT"] + active_stores
        coords = [wh_coord] + [store_coords[s] for s in active_stores]
        n_nodes = len(node_ids)

        dist_matrix = np.zeros((n_nodes, n_nodes))
        for i in range(n_nodes):
            for j in range(i + 1, n_nodes):
                d = haversine_km(coords[i][0], coords[i][1], coords[j][0], coords[j][1])
                dist_matrix[i, j] = d
                dist_matrix[j, i] = d

        # 2. Clarke-Wright Savings Computation
        # S(i, j) = d(0, i) + d(0, j) - d(i, j)
        savings = []
        for i in range(1, n_nodes):
            for j in range(i + 1, n_nodes):
                s_val = dist_matrix[0, i] + dist_matrix[0, j] - dist_matrix[i, j]
                savings.append((s_val, i, j))

        # Sort savings in descending order
        savings.sort(key=lambda x: x[0], reverse=True)

        # Initially, each store has its own dedicated round-trip route: [i]
        routes: List[List[int]] = [[i] for i in range(1, n_nodes)]
        truck_capacity = max(t["capacity"] for t in available_trucks)

        def get_route_demand(route: List[int]) -> float:
            return sum(store_demands[node_ids[idx]] for idx in route)

        # 3. Merge Routes Greedily
        for s_val, i, j in savings:
            # Find routes containing i and j
            r_i = None
            r_j = None
            for r in routes:
                if i in r:
                    r_i = r
                if j in r:
                    r_j = r
            if r_i is None or r_j is None or r_i == r_j:
                continue

            # Can only merge if i and j are at the endpoints of their respective routes
            merged = None
            if r_i[-1] == i and r_j[0] == j:
                merged = r_i + r_j
            elif r_j[-1] == j and r_i[0] == i:
                merged = r_j + r_i
            elif r_i[0] == i and r_j[0] == j:
                merged = list(reversed(r_i)) + r_j
            elif r_i[-1] == i and r_j[-1] == j:
                merged = r_i + list(reversed(r_j))

            if merged and get_route_demand(merged) <= truck_capacity:
                routes.remove(r_i)
                routes.remove(r_j)
                routes.append(merged)

        # 4. Apply 2-Opt Local Search to Untangle Each Route
        optimized_routes = []
        for r in routes:
            improved = self._two_opt(r, dist_matrix)
            optimized_routes.append(improved)

        # 5. Build Final VRPRoute Manifests
        vrp_routes: List[VRPRoute] = []
        unassigned: List[str] = []
        truck_idx = 0

        for r in optimized_routes:
            if truck_idx < len(available_trucks):
                trk = available_trucks[truck_idx]
                truck_idx += 1
            else:
                # No more available trucks
                unassigned.extend([node_ids[idx] for idx in r])
                continue

            stops: List[VRPStop] = []
            prev_idx = 0  # Depot
            cum_dist = 0.0
            cum_cargo = 0.0

            for order_seq, node_idx in enumerate(r, start=1):
                st_id = node_ids[node_idx]
                lat, lon = coords[node_idx]
                d_prev = dist_matrix[prev_idx, node_idx]
                cum_dist += d_prev
                d_qty = store_demands[st_id]
                cum_cargo += d_qty

                stops.append(
                    VRPStop(
                        store_id=st_id,
                        lat=lat,
                        lon=lon,
                        demand_units=d_qty,
                        arrival_order=order_seq,
                        distance_from_prev_km=round(d_prev, 2),
                    )
                )
                prev_idx = node_idx

            # Return to depot distance
            return_dist = dist_matrix[prev_idx, 0]
            cum_dist += return_dist

            fuel_cost = cum_dist * self.fuel_cost_per_km
            salary = trk.get("driver_salary", 150.0)
            transit_hours = cum_dist / self.speed_km_h

            vrp_routes.append(
                VRPRoute(
                    truck_id=trk["id"],
                    warehouse_id=warehouse_id,
                    stops=stops,
                    total_cargo_units=round(cum_cargo, 1),
                    total_distance_km=round(cum_dist, 2),
                    estimated_fuel_cost=round(fuel_cost, 2),
                    driver_salary_share=round(salary, 2),
                    estimated_transit_hours=round(transit_hours, 2),
                )
            )

        elapsed_ms = (time.time() - t0) * 1000
        total_km = sum(r.total_distance_km for r in vrp_routes)
        total_cargo = sum(r.total_cargo_units for r in vrp_routes)

        return VRPDispatchPlan(
            cluster_id=cluster_id,
            warehouse_id=warehouse_id,
            routes=vrp_routes,
            total_distance_km=round(total_km, 2),
            total_cargo_delivered=round(total_cargo, 1),
            unassigned_stores=unassigned,
            execution_time_ms=round(elapsed_ms, 2),
        )

    def _two_opt(self, route: List[int], dist_matrix: np.ndarray) -> List[int]:
        """Iteratively reverses subsegments of the route to eliminate crossing paths."""
        if len(route) <= 2:
            return route

        best_route = list(route)
        improved = True

        def route_length(r: List[int]) -> float:
            dist = dist_matrix[0, r[0]]
            for k in range(len(r) - 1):
                dist += dist_matrix[r[k], r[k + 1]]
            dist += dist_matrix[r[-1], 0]
            return dist

        best_dist = route_length(best_route)

        while improved:
            improved = False
            for i in range(len(best_route) - 1):
                for j in range(i + 1, len(best_route)):
                    # Reverse segment from i to j
                    new_route = best_route[:i] + list(reversed(best_route[i : j + 1])) + best_route[j + 1 :]
                    new_dist = route_length(new_route)
                    if new_dist < best_dist - 1e-4:
                        best_route = new_route
                        best_dist = new_dist
                        improved = True
                        break
                if improved:
                    break

        return best_route
