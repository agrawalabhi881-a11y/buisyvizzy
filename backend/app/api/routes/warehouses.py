"""
backend/app/api/routes/warehouses.py
Warehouse manager endpoints: capacity tracking, order fulfillment, and escalation.
"""

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.auth_service import UserProfile, require_roles
from app.services.warehouse_service import WarehouseService

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.get("/{warehouse_id}")
def get_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    user: UserProfile = Security(require_roles(["ADMIN", "DISTRIBUTOR", "WAREHOUSE_MANAGER"])),
):
    """Inspects warehouse capacity, current stock utilization, and geocoordinates."""
    return WarehouseService.get_warehouse_summary(warehouse_id, db)


@router.post("/{warehouse_id}/fulfill-order/{order_id}")
def fulfill_order(
    warehouse_id: int,
    order_id: int,
    db: Session = Depends(get_db),
    user: UserProfile = Security(require_roles(["ADMIN", "WAREHOUSE_MANAGER"])),
):
    """
    Fulfills an inbound store order:
    - Deducts stock from warehouse inventory
    - Handles shortages and triggers automated escalation to distributor
    - Samples realistic internal handling lead times
    """
    return WarehouseService.fulfill_order(warehouse_id, order_id, db)


@router.post("/{warehouse_id}/escalate-order/{order_id}")
def escalate_order(
    warehouse_id: int,
    order_id: int,
    db: Session = Depends(get_db),
    user: UserProfile = Security(require_roles(["ADMIN", "WAREHOUSE_MANAGER"])),
):
    """Manually or automatically escalates an unfulfillable order back to the distributor."""
    return WarehouseService.escalate_unfulfillable_order(order_id, db)
