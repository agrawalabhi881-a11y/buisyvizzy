"""
backend/app/optimizers/failover.py
Dynamic in-transit breakdown failover and real-time route recovery.
Reassigns unvisited delivery stops to the nearest idle truck in the same geographic cluster.
"""

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from backend.app.optimizers.vrp import VRPRoute, VRPStop, CVRPOptimizer, haversine_km


class FailoverEvent(BaseModel):
    timestamp_tick: int
    broken_truck_id: str
    rescue_truck_id: str
    cluster_id: int
    unvisited_stops_count: int
    rescue_distance_km: float
    total_new_route_km: float
    delay_hours: float
    status: str = "RESOLVED"


class DynamicFailoverEngine:
    """Manages breakdown failovers and real-time route recalculation."""

    def __init__(self, vrp_solver: Optional[CVRPOptimizer] = None):
        self.vrp_solver = vrp_solver or CVRPOptimizer()
        self.failover_history: List[FailoverEvent] = []

    def handle_breakdown_and_reroute(
        self,
        tick: int,
        broken_truck_id: str,
        current_route: VRPRoute,
        completed_stop_indices: List[int],
        cluster_id: int,
        idle_trucks: List[dict],  # list of {'id': str, 'lat': float, 'lon': float, 'capacity': float}
        store_coords: Dict[str, Tuple[float, float]],
    ) -> Optional[Tuple[VRPRoute, FailoverEvent]]:
        """
        When broken_truck_id fails:
          1. Extracts all remaining unvisited stops from current_route.
          2. Finds the nearest idle truck in cluster_id.
          3. Recalculates the optimal VRP route starting from the rescue truck's position.
          4. Returns (new_vrp_route, failover_event).
        """
        all_stops = current_route.stops
        unvisited = [s for idx, s in enumerate(all_stops) if idx not in completed_stop_indices]

        if not unvisited or not idle_trucks:
            return None

        # Last known location of broken truck (or first unvisited stop)
        first_unvisited = unvisited[0]
        broken_lat, broken_lon = first_unvisited.lat, first_unvisited.lon

        # Select closest idle truck
        rescue_truck = min(
            idle_trucks,
            key=lambda t: haversine_km(t["lat"], t["lon"], broken_lat, broken_lon),
        )

        rescue_id = rescue_truck["id"]
        rescue_start_coord = (rescue_truck["lat"], rescue_truck["lon"])
        dist_to_broken = haversine_km(rescue_start_coord[0], rescue_start_coord[1], broken_lat, broken_lon)

        # Prepare demands for remaining stops
        unvisited_demands = {s.store_id: s.demand_units for s in unvisited}
        sub_coords = {s.store_id: (s.lat, s.lon) for s in unvisited}

        # Solve sub-VRP starting from rescue truck
        dispatch_plan = self.vrp_solver.solve_cluster_vrp(
            cluster_id=cluster_id,
            warehouse_id=current_route.warehouse_id,
            wh_coord=rescue_start_coord,
            store_demands=unvisited_demands,
            store_coords=sub_coords,
            available_trucks=[rescue_truck],
        )

        if not dispatch_plan.routes:
            return None

        new_route = dispatch_plan.routes[0]
        new_route.truck_id = rescue_id
        # Add transit distance from rescue base to rendezvous
        new_route.total_distance_km = round(new_route.total_distance_km + dist_to_broken, 2)
        added_delay_hours = round(dist_to_broken / self.vrp_solver.speed_km_h + 1.0, 2)

        event = FailoverEvent(
            timestamp_tick=tick,
            broken_truck_id=broken_truck_id,
            rescue_truck_id=rescue_id,
            cluster_id=cluster_id,
            unvisited_stops_count=len(unvisited),
            rescue_distance_km=round(dist_to_broken, 2),
            total_new_route_km=new_route.total_distance_km,
            delay_hours=added_delay_hours,
            status="RESOLVED",
        )
        self.failover_history.append(event)
        return new_route, event
