"""
backend/app/api/routes/procurement.py
Distributor replenishment endpoints: (s, S) policy evaluation and manufacturing procurement.
"""

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.auth_service import UserProfile, require_roles
from app.services.procurement_service import ProcurementService

router = APIRouter(prefix="/procurement", tags=["Procurement"])


@router.post("/distributors/{distributor_id}/evaluate")
def evaluate_procurement(
    distributor_id: int,
    db: Session = Depends(get_db),
    user: UserProfile = Security(require_roles(["ADMIN", "DISTRIBUTOR"])),
):
    """
    Evaluates the (s, S) replenishment policy across all warehouses:
    Triggers purchase orders to the manufacturer when inventory falls below s.
    """
    orders = ProcurementService.evaluate_sS_procurement(distributor_id, db)
    return {
        "distributor_id": distributor_id,
        "orders_placed_count": len(orders),
        "orders": orders,
    }
