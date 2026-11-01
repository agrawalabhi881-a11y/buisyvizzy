"""
backend/app/services/store_service.py
Core demand node domain service for Store operations:
- Order placement based on store demand
- Real-time order and shipment tracking
- Unmet demand and lost sales logging (critical penalty metric)
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Dict, Optional
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.store import Store
from app.models.order import Order, OrderLine
from app.models.unmet_demand import UnmetDemand
from app.models.product import Product
from app.models.shipment import Shipment


class StoreService:
    """Manages retail store operations, demand tracking, and order lifecycle."""

    @staticmethod
    def place_order(
        store_id: int,
        lines_input: List[Dict[str, float]],
        session: Session,
    ) -> Order:
        store = session.get(Store, store_id)
        if not store:
            raise HTTPException(status_code=404, detail=f"Store {store_id} not found")

        order_num = f"ORD-ST{store_id}-{int(datetime.now(timezone.utc).timestamp())}-{uuid.uuid4().hex[:4].upper()}"

        order = Order(
            order_number=order_num,
            order_type="store_order",
            source_store_id=store.id,
            destination_distributor_id=store.distributor_id,
            status="submitted",
        )
        session.add(order)
        session.flush()

        for item in lines_input:
            p_id = int(item["product_id"])
            qty = float(item["quantity"])
            prod = session.get(Product, p_id)
            if not prod:
                raise HTTPException(status_code=404, detail=f"Product {p_id} not found")

            unit_price = float(prod.unit_price) if hasattr(prod, "unit_price") and prod.unit_price else float(prod.unit_cost) * 1.5

            line = OrderLine(
                order_id=order.id,
                product_id=p_id,
                quantity_requested=Decimal(str(qty)),
                quantity_fulfilled=Decimal("0.0"),
                unit_price=Decimal(str(round(unit_price, 4))),
            )
            session.add(line)

        session.commit()
        session.refresh(order)
        return order

    @staticmethod
    def log_unmet_demand(
        order_id: int,
        store_id: int,
        product_id: int,
        requested_quantity: float,
        fulfilled_quantity: float,
        unmet_quantity: float,
        reason: str = "warehouse_stockout",
        session: Session = None,
    ) -> UnmetDemand:
        """Logs lost sales when customer demand goes unfulfilled."""
        store = session.get(Store, store_id)
        prod = session.get(Product, product_id)
        order = session.get(Order, order_id)
        if not store or not prod or not order:
            raise HTTPException(status_code=404, detail="Store, Product, or Order not found")

        unmet = UnmetDemand(
            order_id=order_id,
            store_id=store_id,
            product_id=product_id,
            requested_quantity=Decimal(str(requested_quantity)),
            fulfilled_quantity=Decimal(str(fulfilled_quantity)),
            unmet_quantity=Decimal(str(unmet_quantity)),
            reason=reason,
        )
        session.add(unmet)
        session.commit()
        session.refresh(unmet)
        return unmet

    @staticmethod
    def track_order(order_number: str, session: Session) -> dict:
        """Tracks the end-to-end status, line fulfillments, and shipments for an order."""
        order = session.scalar(select(Order).where(Order.order_number == order_number))
        if not order:
            raise HTTPException(status_code=404, detail=f"Order {order_number} not found")

        lines_detail = []
        for line in order.lines:
            lines_detail.append({
                "product_id": line.product_id,
                "requested": float(line.quantity_requested),
                "fulfilled": float(line.quantity_fulfilled),
                "backordered": float(line.backorder.remaining_quantity) if line.backorder else 0.0,
            })

        shipments_detail = []
        for s in order.shipments:
            shipments_detail.append({
                "shipment_number": s.shipment_number,
                "status": s.status,
                "truck_id": s.truck_id,
                "shipped_at": s.shipped_at.isoformat() if s.shipped_at else None,
                "estimated_arrival": s.estimated_arrival.isoformat() if s.estimated_arrival else None,
            })

        return {
            "order_number": order.order_number,
            "status": order.status,
            "store_id": order.source_store_id,
            "order_date": order.order_date.isoformat() if order.order_date else None,
            "lines": lines_detail,
            "shipments": shipments_detail,
        }
