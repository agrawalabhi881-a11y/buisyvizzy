"""
backend/app/services/procurement_service.py
Core replenishment domain service:
- Evaluates the (s, S) replenishment policy
- Aggregates inventory positions across regional warehouses
- Triggers upstream purchase procurement orders to the Manufacturer
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Dict
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.distributor import Distributor
from app.models.warehouse import Warehouse
from app.models.inventory import Inventory
from app.models.order import Order, OrderLine
from app.models.product import Product
from app.services.warehouse_service import WarehouseService


class ProcurementService:
    """Manages aggregate distributor replenishment and upstream supplier procurement."""

    @staticmethod
    def evaluate_sS_procurement(distributor_id: int, session: Session) -> List[dict]:
        distributor = session.get(Distributor, distributor_id)
        if not distributor:
            raise HTTPException(status_code=404, detail=f"Distributor {distributor_id} not found")

        placed_orders = []

        warehouses = session.scalars(
            select(Warehouse).where(Warehouse.distributor_id == distributor_id)
        ).all()

        for wh in warehouses:
            wh_summary = WarehouseService.get_warehouse_summary(wh.id, session)
            available_cap = wh_summary["available_capacity"]

            inventories = session.scalars(
                select(Inventory).where(Inventory.warehouse_id == wh.id)
            ).all()

            for inv in inventories:
                current = float(inv.quantity_on_hand)
                reserved = float(inv.quantity_reserved)
                pos = current - reserved
                s = float(inv.reorder_level)
                S = float(inv.maximum_stock_level) if inv.maximum_stock_level else s * 3.0

                if pos <= s and S > pos:
                    needed = S - pos
                    order_qty = min(needed, available_cap)

                    if order_qty >= 1.0:
                        prod = session.get(Product, inv.product_id)
                        unit_cost = float(prod.unit_cost) if prod else 10.0

                        order_num = f"PO-DIST{distributor_id}-WH{wh.id}-{int(datetime.now(timezone.utc).timestamp())}-{uuid.uuid4().hex[:4].upper()}"
                        po = Order(
                            order_number=order_num,
                            order_type="procurement",
                            source_distributor_id=distributor.id,
                            destination_manufacturer_id=distributor.manufacturer_id,
                            status="submitted",
                        )
                        session.add(po)
                        session.flush()

                        line = OrderLine(
                            order_id=po.id,
                            product_id=inv.product_id,
                            quantity_requested=Decimal(str(round(order_qty, 3))),
                            quantity_fulfilled=Decimal("0.0"),
                            unit_price=Decimal(str(round(unit_cost, 4))),
                        )
                        session.add(line)

                        available_cap -= order_qty

                        placed_orders.append({
                            "order_number": order_num,
                            "warehouse_id": wh.id,
                            "product_id": inv.product_id,
                            "quantity_ordered": order_qty,
                            "policy": f"(s={s}, S={S}) triggered at position={pos}",
                        })

        session.commit()
        return placed_orders
