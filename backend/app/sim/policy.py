"""
backend/app/sim/policy.py
Inventory replenishment policies.
Implements the baseline (s, S) policy for upstream manufacturing orders
and store reorder triggers, providing the benchmark against which optimization is evaluated.
"""

from typing import Dict, List, Tuple
from contracts.models import NodeRole
from backend.app.sim.network import NetworkState, NodeState


class ReplenishmentPolicy:
    """Evaluates inventory positions and determines reorder decisions."""

    @staticmethod
    def evaluate_upstream_sS_policy(
        network: NetworkState,
    ) -> List[Tuple[str, str, float]]:
        """
        Distributor Baseline Upstream Policy:
        For each warehouse and product:
          Inventory Position = current_stock + in_transit_inbound - reserved_stock.
          If Inventory Position <= s (reorder_point):
            Order Q = max(0, S - Inventory Position) up to available physical warehouse capacity.
        Returns:
          List of (warehouse_id, product_id, reorder_quantity)
        """
        orders_to_place: List[Tuple[str, str, float]] = []

        # Calculate in-transit inbound units per (warehouse_id, product_id)
        inbound_pipeline: Dict[Tuple[str, str], float] = {}
        for shipment in network.active_shipments.values():
            wh_id = shipment.destination_id
            for line in shipment.lines:
                key = (wh_id, line.product_id)
                inbound_pipeline[key] = inbound_pipeline.get(key, 0.0) + line.ordered_units

        for node in network.nodes.values():
            if node.role != NodeRole.WAREHOUSE:
                continue

            available_node_capacity = node.remaining_capacity
            for product_id, inv in node.inventory.items():
                inbound_units = inbound_pipeline.get((node.id, product_id), 0.0)
                inventory_position = inv.current_stock + inbound_units - inv.reserved_stock

                if inventory_position <= inv.reorder_point:
                    raw_qty = inv.order_up_to - inventory_position
                    # Respect warehouse capacity limits
                    capped_qty = min(raw_qty, available_node_capacity)
                    if capped_qty > 0:
                        orders_to_place.append((node.id, product_id, round(capped_qty, 1)))
                        available_node_capacity -= capped_qty

        return orders_to_place

    @staticmethod
    def evaluate_store_replenishment(
        store: NodeState,
        product_id: str,
        demanded_units: float,
    ) -> float:
        """
        Determines the quantity a store orders from its primary warehouse.
        In the standard baseline, the store immediately orders the units demanded by consumers.
        """
        return max(0.0, demanded_units)
