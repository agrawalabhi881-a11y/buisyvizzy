"""
backend/app/services/warehouse_service.py
Core physical node domain service for Warehouse operations:
- Capacity enforcement
- Real-time stock reservation and deduction
- Stochastic handling lead-time sampling
- Order fulfillment and automated escalation
"""

from decimal import Decimal
import random
from typing import Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.warehouse import Warehouse
from app.models.inventory import Inventory
from app.models.order import Order, OrderLine, Backorder
from app.models.product import Product


class WarehouseService:
    """Manages physical storage nodes, capacity, fulfillment, and escalation."""

    @staticmethod
    def get_warehouse_summary(warehouse_id: int, session: Session) -> dict:
        wh = session.get(Warehouse, warehouse_id)
        if not wh:
            raise HTTPException(status_code=404, detail=f"Warehouse {warehouse_id} not found")

        current_usage = session.scalar(
            select(func.coalesce(func.sum(Inventory.quantity_on_hand * Product.storage_units_per_item), 0))
            .join(Product, Product.id == Inventory.product_id)
            .where(Inventory.warehouse_id == warehouse_id)
        ) or 0.0

        return {
            "warehouse_id": wh.id,
            "name": wh.name,
            "location": wh.location,
            "latitude": wh.latitude,
            "longitude": wh.longitude,
            "storage_capacity": float(wh.storage_capacity),
            "current_usage": float(current_usage),
            "utilization_pct": round(float(current_usage) / float(wh.storage_capacity) * 100, 2)
            if float(wh.storage_capacity) > 0 else 0.0,
            "available_capacity": max(0.0, float(wh.storage_capacity) - float(current_usage)),
        }

    @staticmethod
    def check_capacity(warehouse_id: int, additional_units: float, session: Session) -> bool:
        summary = WarehouseService.get_warehouse_summary(warehouse_id, session)
        return summary["available_capacity"] >= additional_units

    @staticmethod
    def sample_processing_lead_time_hours() -> float:
        """Samples internal warehouse pick-and-pack lead time (lognormal distribution)."""
        return round(float(random.lognormvariate(0.7, 0.3)), 2)

    @staticmethod
    def fulfill_order(warehouse_id: int, order_id: int, session: Session) -> dict:
        order = session.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

        lines_report = []
        has_shortage = False
        all_empty = True

        for line in order.lines:
            inv = session.scalar(
                select(Inventory).where(
                    Inventory.warehouse_id == warehouse_id,
                    Inventory.product_id == line.product_id,
                )
            )

            available = float(inv.quantity_on_hand - inv.quantity_reserved) if inv else 0.0
            requested = float(line.quantity_requested)
            fulfillable = min(requested, max(0.0, available))
            shortage = requested - fulfillable

            if fulfillable > 0 and inv:
                all_empty = False
                inv.quantity_on_hand -= Decimal(str(fulfillable))
                line.quantity_fulfilled += Decimal(str(fulfillable))

            if shortage > 0:
                has_shortage = True
                if not line.backorder:
                    bo = Backorder(
                        order_line_id=line.id,
                        remaining_quantity=Decimal(str(shortage)),
                        status="open",
                    )
                    session.add(bo)
                else:
                    line.backorder.remaining_quantity = Decimal(str(shortage))

            lines_report.append({
                "product_id": line.product_id,
                "requested": requested,
                "fulfilled": fulfillable,
                "shortage": shortage,
            })

        if not has_shortage:
            order.status = "fulfilled"
        elif all_empty:
            order.status = "submitted"
        else:
            order.status = "partially_fulfilled"

        handling_hours = WarehouseService.sample_processing_lead_time_hours()
        session.commit()

        return {
            "order_id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "has_shortage": has_shortage,
            "processing_lead_time_hours": handling_hours,
            "lines": lines_report,
        }

    @staticmethod
    def escalate_unfulfillable_order(order_id: int, session: Session) -> dict:
        order = session.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

        order.status = "submitted"
        session.commit()
        return {
            "order_id": order.id,
            "status": "escalated_to_distributor",
            "message": f"Order {order.order_number} escalated to distributor {order.destination_distributor_id}",
        }
