"""
backend/app/sim/transit.py
Stochastic transit simulation with Monte Carlo lead-time sampling.
Implements lognormal heavy-tail distributions, warehouse processing delays,
and dynamic truck breakdown / cluster failover logic.
"""

from typing import Optional, Tuple, List
import numpy as np
from contracts.models import TruckStatus, OrderStatus
from backend.app.sim.network import NetworkState, TruckState, ShipmentState


class TransitEngine:
    """Manages stochastic transit times, lead-time sampling, and truck failover."""

    def __init__(self, rng: Optional[np.random.Generator] = None, seed: int = 42):
        self.rng = rng or np.random.default_rng(seed)
        # Baseline breakdown probability per trip (e.g. 2% chance of mid-transit failure)
        self.breakdown_probability: float = 0.02

    def sample_lead_time_ticks(
        self,
        distance_km: float,
        speed_km_h: float = 55.0,
        lane_delay_factor: float = 1.0,
    ) -> int:
        """
        Calculates stochastic transit time in simulation ticks (days).
        Uses a lognormal distribution to model realistic heavy-tail traffic / weather delays.
        """
        # Nominal travel hours
        nominal_hours = max(1.0, distance_km / speed_km_h)
        nominal_days = nominal_hours / 10.0  # assume 10 driving hours per tick/day

        # Lognormal noise with mu=0, sigma=0.35 creates right-skewed heavy tail
        stochastic_multiplier = float(self.rng.lognormal(mean=0.0, sigma=0.35))
        effective_days = nominal_days * stochastic_multiplier * lane_delay_factor

        # Minimum transit time is 1 tick
        transit_ticks = int(max(1, round(effective_days)))
        return transit_ticks

    def sample_warehouse_processing_time(self) -> int:
        """Samples internal warehouse picking & packaging lead time (0 or 1 tick)."""
        # 80% same tick (0 ticks extra), 20% backlog (+1 tick)
        return int(self.rng.choice([0, 1], p=[0.80, 0.20]))

    def sample_manufacturer_lead_time(self, supplier_delay_factor: float = 1.0) -> int:
        """
        Upstream manufacturing replenishment lead time:
        Typically 3-7 ticks, heavy-tailed under disruption.
        """
        base_days = float(self.rng.integers(3, 7))
        heavy_tail_delay = float(self.rng.lognormal(mean=0.0, sigma=0.25))
        total_ticks = int(max(2, round(base_days * heavy_tail_delay * supplier_delay_factor)))
        return total_ticks

    def check_for_breakdown(self) -> bool:
        """Determines if a truck experiences a mechanical breakdown on a trip."""
        return bool(self.rng.random() < self.breakdown_probability)

    def execute_failover(
        self,
        broken_truck: TruckState,
        shipment: ShipmentState,
        network: NetworkState,
    ) -> Optional[TruckState]:
        """
        Failover Cluster Logic:
        If a truck breaks down in transit:
          1. Mark broken truck as BROKEN_DOWN.
          2. Scan all IDLE trucks in the same geographic cluster.
          3. Dispatch the nearest available idle truck in that cluster to rescue the cargo.
        """
        broken_truck.status = TruckStatus.BROKEN_DOWN
        cluster_id = broken_truck.cluster_id

        # Find idle trucks in the same cluster
        candidate_trucks = [
            t for t in network.trucks.values()
            if t.cluster_id == cluster_id and t.status == TruckStatus.IDLE and t.id != broken_truck.id
        ]

        if not candidate_trucks:
            # Fallback: check any idle truck in adjacent clusters
            candidate_trucks = [
                t for t in network.trucks.values()
                if t.status == TruckStatus.IDLE and t.id != broken_truck.id
            ]

        if not candidate_trucks:
            # No available truck; shipment remains delayed in transit
            return None

        # Choose closest truck to the broken truck's coordinates
        replacement_truck = min(
            candidate_trucks,
            key=lambda t: (t.current_lat - broken_truck.current_lat) ** 2
            + (t.current_lon - broken_truck.current_lon) ** 2,
        )

        # Reassign shipment
        replacement_truck.status = TruckStatus.IN_TRANSIT
        replacement_truck.current_shipment_id = shipment.id
        shipment.truck_id = replacement_truck.id

        # Add 1 tick penalty for rescue & transfer
        shipment.expected_arrival_tick += 1
        return replacement_truck
