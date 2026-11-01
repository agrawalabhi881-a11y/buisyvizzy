"""
backend/app/sim/engine.py
SimPy-powered discrete-event supply chain simulation engine.
Executes the Diagram 3 tick loop with deterministic seed reproducibility.
"""

from typing import Dict, List, Optional, Tuple
import simpy
import numpy as np

from contracts.models import (
    NodeRole,
    OrderStatus,
    TruckStatus,
    KPISnapshotContract,
    ProductContract,
    NodeContract,
    TruckContract,
    InventoryContract,
)
from backend.app.sim.network import (
    NetworkState,
    InventoryState,
    OrderState,
    OrderLineState,
    ShipmentState,
    TruckState,
)
from backend.app.sim.demand import DemandGenerator
from backend.app.sim.transit import TransitEngine
from backend.app.sim.policy import ReplenishmentPolicy
from backend.app.sim.disruptions import DisruptionEngine
from backend.app.sim.kpi import KPIAccruer
from backend.app.optimizers.rebalance import WarehouseRebalanceOptimizer


class SupplyChainSimulationEngine:
    """The central digital twin simulation engine."""

    def __init__(self, seed: int = 42, optimizer_enabled: bool = False):
        self.seed = seed
        self.optimizer_enabled = optimizer_enabled
        # Independent RNG streams for CRN (Common Random Numbers) synchronization
        self.demand_rng = np.random.default_rng(seed)
        self.transit_rng = np.random.default_rng(seed + 10000)

        # Domain components
        self.network = NetworkState()
        self.demand_gen = DemandGenerator(rng=self.demand_rng, seed=seed)
        self.transit_engine = TransitEngine(rng=self.transit_rng, seed=seed + 10000)
        self.disruption_engine = DisruptionEngine()
        self.kpi_accruer = KPIAccruer()
        self.rebalance_optimizer = WarehouseRebalanceOptimizer()

        self.env = simpy.Environment()
        self.current_tick: int = 0
        self._order_counter: int = 0
        self._shipment_counter: int = 0
        self.rebalancing_history = []

    def initialize_network(
        self,
        products: List[ProductContract],
        nodes: List[NodeContract],
        trucks: List[TruckContract],
        inventories: List[InventoryContract],
    ):
        """Initializes network topology, products, inventory, and logistics fleet."""
        self.network.load_from_contracts(products, nodes, trucks, inventories)

    # -------------------------------------------------------------------------
    # Core Diagram 3: Tick Execution Loop
    # -------------------------------------------------------------------------
    def run_tick(self) -> KPISnapshotContract:
        """
        Advances the world by exactly 1 tick (day), executing the 9 canonical steps.
        """
        t = self.current_tick
        tick_demanded_units = 0.0
        tick_fulfilled_units = 0.0
        tick_unmet_units = 0.0
        tick_unmet_cost = 0.0
        tick_revenue = 0.0
        tick_procurement_cost = 0.0
        tick_transport_fuel = 0.0

        # Step 2: Disruption Check / Injection
        active_disruptions = self.disruption_engine.update_disruptions_for_tick(t)

        # Step 3: Inbound Shipments Arrival & Processing
        arrived_shipment_ids = []
        for s_id, shipment in list(self.network.active_shipments.items()):
            if shipment.expected_arrival_tick <= t:
                # Deliver cargo to destination node
                dest_node = self.network.nodes.get(shipment.destination_id)
                if dest_node:
                    for line in shipment.lines:
                        if line.product_id not in dest_node.inventory:
                            dest_node.inventory[line.product_id] = InventoryState(
                                node_id=dest_node.id,
                                product_id=line.product_id,
                                current_stock=0.0,
                            )
                        # Add delivered units to stock
                        dest_node.inventory[line.product_id].current_stock += line.ordered_units

                # Release assigned truck back to IDLE
                if shipment.truck_id and shipment.truck_id in self.network.trucks:
                    truck = self.network.trucks[shipment.truck_id]
                    if truck.status != TruckStatus.BROKEN_DOWN:
                        truck.status = TruckStatus.IDLE
                    truck.current_shipment_id = None

                shipment.status = OrderStatus.DELIVERED
                self.network.delivered_shipments.append(shipment)
                arrived_shipment_ids.append(s_id)

        for s_id in arrived_shipment_ids:
            del self.network.active_shipments[s_id]

        # Step 4 & 5: Store Customer Demand & Order Placement
        # Stores receive demand and emit orders to their assigned warehouse
        for store_id, wh_id in self.network.store_to_warehouse.items():
            store = self.network.nodes[store_id]
            order_lines: List[OrderLineState] = []

            for prod_id, prod in self.network.products.items():
                spike_multiplier = self.disruption_engine.get_demand_spike_multiplier(
                    store_id, prod_id
                )
                demanded = self.demand_gen.sample_demand(
                    store_id=store_id,
                    product_id=prod_id,
                    category=prod.category,
                    tick=t,
                    disruption_multiplier=spike_multiplier,
                )
                if demanded > 0:
                    tick_demanded_units += demanded
                    ordered_qty = ReplenishmentPolicy.evaluate_store_replenishment(
                        store, prod_id, demanded
                    )
                    order_lines.append(
                        OrderLineState(
                            product_id=prod_id,
                            ordered_units=ordered_qty,
                            fulfilled_units=0.0,
                            unmet_units=0.0,
                        )
                    )

            if not order_lines:
                continue

            self._order_counter += 1
            order_id = f"ORD_{self._order_counter:06d}"
            order = OrderState(
                id=order_id,
                store_id=store_id,
                warehouse_id=wh_id,
                status=OrderStatus.PENDING,
                created_tick=t,
                lines=order_lines,
            )
            self.network.orders[order_id] = order
            self.kpi_accruer.total_order_events += 1

            # Step 6: Warehouse Order Fulfillment
            wh = self.network.nodes.get(wh_id)
            is_operational = self.disruption_engine.is_warehouse_operational(wh_id)
            had_stockout = False
            total_cargo_to_ship = 0.0
            shipment_lines: List[OrderLineState] = []

            for line in order.lines:
                prod = self.network.products[line.product_id]
                inv = wh.inventory.get(line.product_id) if (wh and is_operational) else None

                available = inv.available_stock if inv else 0.0
                fulfillable = min(line.ordered_units, available)
                unmet = line.ordered_units - fulfillable

                line.fulfilled_units = fulfillable
                line.unmet_units = unmet
                tick_fulfilled_units += fulfillable

                if fulfillable > 0 and inv:
                    inv.current_stock -= fulfillable
                    total_cargo_to_ship += fulfillable
                    shipment_lines.append(
                        OrderLineState(
                            product_id=line.product_id,
                            ordered_units=fulfillable,
                            fulfilled_units=fulfillable,
                        )
                    )
                    tick_revenue += fulfillable * prod.unit_price

                if unmet > 0:
                    had_stockout = True
                    tick_unmet_units += unmet
                    tick_unmet_cost += unmet * prod.unmet_demand_penalty

            if had_stockout:
                self.kpi_accruer.stockout_order_events += 1
                order.status = (
                    OrderStatus.PARTIAL if total_cargo_to_ship > 0 else OrderStatus.ESCALATED
                )
            else:
                order.status = OrderStatus.PROCESSING

            # Dispatch Shipment if cargo is available
            if total_cargo_to_ship > 0:
                dist_km = self.network.get_distance(wh_id, store_id)
                # Select available truck in warehouse's cluster
                avail_trucks = [
                    trk for trk in self.network.trucks.values()
                    if trk.cluster_id == wh.cluster_id and trk.status == TruckStatus.IDLE
                ]
                assigned_truck = avail_trucks[0] if avail_trucks else None

                transit_delay = self.disruption_engine.get_transit_delay_factor(wh_id, store_id)
                transit_lead_ticks = self.transit_engine.sample_lead_time_ticks(
                    distance_km=dist_km,
                    speed_km_h=assigned_truck.speed_km_per_hour if assigned_truck else 55.0,
                    lane_delay_factor=transit_delay,
                )
                internal_processing = self.transit_engine.sample_warehouse_processing_time()
                arrival_tick = t + transit_lead_ticks + internal_processing

                self._shipment_counter += 1
                shipment_id = f"SHIP_{self._shipment_counter:06d}"
                shipment = ShipmentState(
                    id=shipment_id,
                    order_id=order.id,
                    origin_id=wh_id,
                    destination_id=store_id,
                    truck_id=assigned_truck.id if assigned_truck else None,
                    dispatch_tick=t + internal_processing,
                    expected_arrival_tick=arrival_tick,
                    distance_km=dist_km,
                    cargo_units=total_cargo_to_ship,
                    status=OrderStatus.IN_TRANSIT,
                    lines=shipment_lines,
                )
                self.network.active_shipments[shipment_id] = shipment

                if assigned_truck:
                    assigned_truck.status = TruckStatus.IN_TRANSIT
                    assigned_truck.current_shipment_id = shipment_id
                    assigned_truck.total_km_travelled += dist_km
                    fuel_cost = dist_km * assigned_truck.fuel_cost_per_km
                    assigned_truck.total_fuel_cost += fuel_cost
                    tick_transport_fuel += fuel_cost

        # Step 7: Distributor Replenishment & Rebalancing Planning
        if self.optimizer_enabled:
            wh_nodes = {
                w_id: {"capacity": n.max_capacity_units, "current_stock": n.total_current_stock}
                for w_id, n in self.network.nodes.items()
                if n.role == NodeRole.WAREHOUSE
            }
            inv_map = {
                (w_id, p_id): {
                    "stock": inv.current_stock,
                    "safety": inv.safety_stock,
                    "reorder": inv.reorder_point,
                }
                for w_id, n in self.network.nodes.items()
                if n.role == NodeRole.WAREHOUSE
                for p_id, inv in n.inventory.items()
            }
            prod_map = {
                p_id: {"penalty": p.unmet_demand_penalty, "unit_cost": p.unit_cost}
                for p_id, p in self.network.products.items()
            }
            dist_map = {
                (w1, w2): self.network.get_distance(w1, w2)
                for w1 in wh_nodes
                for w2 in wh_nodes
            }

            rebal_plan = self.rebalance_optimizer.solve_rebalancing(
                tick=t,
                warehouses=wh_nodes,
                inventories=inv_map,
                products=prod_map,
                distance_matrix=dist_map,
            )
            self.rebalancing_history.append(rebal_plan)

            for trf in rebal_plan.transfers:
                src_wh = self.network.nodes.get(trf.from_warehouse_id)
                src_inv = src_wh.inventory.get(trf.product_id) if src_wh else None
                if src_inv and src_inv.current_stock >= trf.quantity_units:
                    src_inv.current_stock -= trf.quantity_units
                    self._shipment_counter += 1
                    trf_ship_id = f"TRF_SHIP_{self._shipment_counter:06d}"
                    trf_shipment = ShipmentState(
                        id=trf_ship_id,
                        order_id=f"REBAL_{t}_{trf.from_warehouse_id}_{trf.to_warehouse_id}",
                        origin_id=trf.from_warehouse_id,
                        destination_id=trf.to_warehouse_id,
                        truck_id=None,
                        dispatch_tick=t,
                        expected_arrival_tick=t + 1,  # Express transfer arrives next tick
                        distance_km=trf.distance_km,
                        cargo_units=trf.quantity_units,
                        status=OrderStatus.IN_TRANSIT,
                        lines=[
                            OrderLineState(
                                product_id=trf.product_id,
                                ordered_units=trf.quantity_units,
                                fulfilled_units=trf.quantity_units,
                            )
                        ],
                    )
                    self.network.active_shipments[trf_ship_id] = trf_shipment
                    tick_transport_fuel += trf.estimated_freight_cost

        # Upstream Manufacturing Replenishment ((s, S) Upstream Policy)
        upstream_orders = ReplenishmentPolicy.evaluate_upstream_sS_policy(self.network)
        supplier_delay = self.disruption_engine.get_supplier_delay_factor("MFR_01")

        for wh_id, prod_id, order_qty in upstream_orders:
            prod = self.network.products[prod_id]
            lead_ticks = self.transit_engine.sample_manufacturer_lead_time(
                supplier_delay_factor=supplier_delay
            )
            proc_cost = order_qty * prod.unit_cost
            tick_procurement_cost += proc_cost

            self._shipment_counter += 1
            mfr_shipment_id = f"MFR_SHIP_{self._shipment_counter:06d}"
            mfr_shipment = ShipmentState(
                id=mfr_shipment_id,
                order_id=f"MFR_PO_{t}_{wh_id}_{prod_id}",
                origin_id="MFR_01",
                destination_id=wh_id,
                truck_id=None,  # Dedicated supplier freight
                dispatch_tick=t,
                expected_arrival_tick=t + lead_ticks,
                distance_km=300.0,
                cargo_units=order_qty,
                status=OrderStatus.IN_TRANSIT,
                lines=[
                    OrderLineState(
                        product_id=prod_id,
                        ordered_units=order_qty,
                        fulfilled_units=order_qty,
                    )
                ],
            )
            self.network.active_shipments[mfr_shipment_id] = mfr_shipment

        # Step 8: Truck Transit Progression & Breakdown Failover
        for shipment in list(self.network.active_shipments.values()):
            if shipment.truck_id and shipment.truck_id in self.network.trucks:
                truck = self.network.trucks[shipment.truck_id]
                # Check for breakdown only if currently in transit and not already broken
                if truck.status == TruckStatus.IN_TRANSIT and self.transit_engine.check_for_breakdown():
                    # Dynamic Failover: reassign to nearest idle truck in cluster
                    self.transit_engine.execute_failover(truck, shipment, self.network)

        # Step 9: KPI Accrual & Snapshot
        snapshot = self.kpi_accruer.record_tick_kpis(
            tick=t,
            network=self.network,
            tick_demanded_units=tick_demanded_units,
            tick_fulfilled_units=tick_fulfilled_units,
            tick_unmet_units=tick_unmet_units,
            tick_unmet_cost=tick_unmet_cost,
            tick_revenue=tick_revenue,
            tick_procurement_cost=tick_procurement_cost,
            tick_transport_fuel=tick_transport_fuel,
            active_disruptions_count=len(active_disruptions),
        )

        # Check disruption recovery
        self.disruption_engine.check_recovery(t, snapshot.fill_rate)

        # Advance tick
        self.current_tick += 1
        return snapshot

    def run_simpy_simulation(self, total_ticks: int = 30) -> List[KPISnapshotContract]:
        """
        Runs the simulation wrapped inside a SimPy process loop.
        Allows seamless discrete-event scheduling.
        """
        snapshots = []

        def sim_process(env: simpy.Environment):
            for _ in range(total_ticks):
                snap = self.run_tick()
                snapshots.append(snap)
                yield env.timeout(1)

        self.env.process(sim_process(self.env))
        self.env.run(until=total_ticks)
        return snapshots
