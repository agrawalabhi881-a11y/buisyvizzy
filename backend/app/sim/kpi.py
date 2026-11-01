"""
backend/app/sim/kpi.py
Real-time KPI accrual and metrics calculation.
Captures system financial and operational health per tick.
"""

from typing import List, Dict
from contracts.models import KPISnapshotContract, NodeRole
from backend.app.sim.network import NetworkState, OrderState


class KPIAccruer:
    """Accumulates costs, service levels, and operational metrics per simulation tick."""

    def __init__(self):
        self.snapshots: List[KPISnapshotContract] = []
        # Cumulative metrics
        self.cum_revenue: float = 0.0
        self.cum_procurement_cost: float = 0.0
        self.cum_holding_cost: float = 0.0
        self.cum_transport_cost: float = 0.0
        self.cum_unmet_cost: float = 0.0
        self.cum_overhead_cost: float = 0.0

        self.cum_demanded_units: float = 0.0
        self.cum_fulfilled_units: float = 0.0
        self.cum_unmet_units: float = 0.0

        self.total_order_events: int = 0
        self.stockout_order_events: int = 0

    def record_tick_kpis(
        self,
        tick: int,
        network: NetworkState,
        tick_demanded_units: float,
        tick_fulfilled_units: float,
        tick_unmet_units: float,
        tick_unmet_cost: float,
        tick_revenue: float,
        tick_procurement_cost: float,
        tick_transport_fuel: float,
        active_disruptions_count: int,
    ) -> KPISnapshotContract:
        """Computes comprehensive daily financial and logistics snapshot."""
        # 1. Accrue Holding Costs across all nodes & products
        tick_holding_cost = 0.0
        for node in network.nodes.values():
            for prod_id, inv in node.inventory.items():
                prod = network.products.get(prod_id)
                rate = prod.holding_cost_per_day if prod else 0.05
                tick_holding_cost += inv.current_stock * rate

        # 2. Daily fixed facility overheads
        tick_facility_overhead = sum(
            node.operating_cost_per_day for node in network.nodes.values()
        )

        # 3. Daily driver salaries
        tick_driver_salary = sum(
            truck.driver_daily_salary for truck in network.trucks.values()
        )
        tick_total_transport = tick_transport_fuel + tick_driver_salary

        # Update cumulative counters
        self.cum_revenue += tick_revenue
        self.cum_procurement_cost += tick_procurement_cost
        self.cum_holding_cost += tick_holding_cost
        self.cum_transport_cost += tick_total_transport
        self.cum_unmet_cost += tick_unmet_cost
        self.cum_overhead_cost += tick_facility_overhead

        self.cum_demanded_units += tick_demanded_units
        self.cum_fulfilled_units += tick_fulfilled_units
        self.cum_unmet_units += tick_unmet_units

        # Operating cost = Procurement + Holding + Transport + Facility Overhead + Unmet Penalty
        total_operating_cost = (
            self.cum_procurement_cost
            + self.cum_holding_cost
            + self.cum_transport_cost
            + self.cum_overhead_cost
            + self.cum_unmet_cost
        )
        net_profit = self.cum_revenue - total_operating_cost

        # Service Level Metrics
        fill_rate = (
            (self.cum_fulfilled_units / self.cum_demanded_units)
            if self.cum_demanded_units > 0
            else 1.0
        )
        stockout_freq = (
            (self.stockout_order_events / self.total_order_events)
            if self.total_order_events > 0
            else 0.0
        )

        snapshot = KPISnapshotContract(
            tick=tick,
            total_revenue=round(self.cum_revenue, 2),
            total_procurement_cost=round(self.cum_procurement_cost, 2),
            total_holding_cost=round(self.cum_holding_cost, 2),
            total_transport_cost=round(self.cum_transport_cost, 2),
            total_unmet_demand_cost=round(self.cum_unmet_cost, 2),
            total_operating_cost=round(total_operating_cost, 2),
            net_profit=round(net_profit, 2),
            total_demanded_units=round(self.cum_demanded_units, 1),
            total_fulfilled_units=round(self.cum_fulfilled_units, 1),
            total_unmet_units=round(self.cum_unmet_units, 1),
            fill_rate=round(fill_rate, 4),
            stockout_frequency=round(stockout_freq, 4),
            active_disruptions_count=active_disruptions_count,
            network_in_recovery=(active_disruptions_count > 0 or fill_rate < 0.95),
        )
        self.snapshots.append(snapshot)
        return snapshot
