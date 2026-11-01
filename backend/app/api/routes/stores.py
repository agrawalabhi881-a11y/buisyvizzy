"""
backend/app/api/routes/stores.py
Store owner endpoints: order placement, order tracking, and unmet demand logging.
"""

from typing import List
from fastapi import APIRouter, Depends, Security
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.auth_service import UserProfile, require_roles
from app.services.store_service import StoreService

router = APIRouter(prefix="/stores", tags=["Stores"])


class OrderLineInput(BaseModel):
    product_id: int
    quantity: float


class PlaceOrderRequest(BaseModel):
    lines: List[OrderLineInput]


class UnmetDemandRequest(BaseModel):
    product_id: int
    unmet_quantity: float
    reason: str = "warehouse_stockout"


@router.post("/{store_id}/orders")
def place_order(
    store_id: int,
    request: PlaceOrderRequest,
    db: Session = Depends(get_db),
    user: UserProfile = Security(require_roles(["ADMIN", "STORE_OWNER"])),
):
    """Places a new store order based on customer demand."""
    order = StoreService.place_order(
        store_id=store_id,
        lines_input=[{"product_id": l.product_id, "quantity": l.quantity} for l in request.lines],
        session=db,
    )
    return {
        "order_id": order.id,
        "order_number": order.order_number,
        "status": order.status,
        "store_id": order.source_store_id,
        "lines_count": len(order.lines),
    }


@router.post("/{store_id}/unmet-demand")
def log_unmet_demand(
    store_id: int,
    request: UnmetDemandRequest,
    db: Session = Depends(get_db),
    user: UserProfile = Security(require_roles(["ADMIN", "STORE_OWNER"])),
):
    """Logs unmet demand and lost sales when an order cannot be fulfilled."""
    record = StoreService.log_unmet_demand(
        store_id=store_id,
        product_id=request.product_id,
        unmet_quantity=request.unmet_quantity,
        reason=request.reason,
        session=db,
    )
    return {
        "unmet_demand_id": record.id,
        "store_id": record.store_id,
        "product_id": record.product_id,
        "unmet_quantity": float(record.unmet_quantity),
        "estimated_lost_revenue": float(record.estimated_lost_revenue),
    }


@router.get("/orders/{order_number}/track")
def track_order(
    order_number: str,
    db: Session = Depends(get_db),
    user: UserProfile = Security(require_roles(["ADMIN", "STORE_OWNER", "DISTRIBUTOR", "TRUCK_DRIVER"])),
):
    """Tracks live order fulfillment and inbound shipment status."""
    return StoreService.track_order(order_number, db)
