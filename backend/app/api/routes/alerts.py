"""
backend/app/api/routes/alerts.py
REST endpoints for Alerts, Autonomous Recommendations, and Activity Audit Trails.
"""

from typing import List, Optional
from fastapi import APIRouter, Security, HTTPException
from pydantic import BaseModel

from app.services.auth_service import UserProfile, require_roles_or_demo
from app.services.alert_service import AlertService
from app.api.routes.simulation import get_or_create_live_engine
from contracts.models import AlertContract, RecommendationContract, ActivityContract

router = APIRouter(tags=["Alerts & Autonomous Recommendations"])
alert_service = AlertService()


@router.get("/alerts", response_model=List[AlertContract])
def list_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR", "WAREHOUSE_MANAGER", "STORE_OWNER", "TRUCK_DRIVER"])),
):
    """Returns active, acknowledged, or resolved operational alerts."""
    return alert_service.get_alerts(status=status, severity=severity)


@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertContract)
def acknowledge_alert(
    alert_id: str,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR", "WAREHOUSE_MANAGER", "STORE_OWNER", "TRUCK_DRIVER"])),
):
    """Operator acknowledges an operational alert."""
    alert = alert_service.acknowledge_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    return alert


@router.post("/alerts/{alert_id}/resolve", response_model=AlertContract)
def resolve_alert(
    alert_id: str,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR", "WAREHOUSE_MANAGER"])),
):
    """Operator resolves an operational alert."""
    alert = alert_service.resolve_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    return alert


@router.get("/recommendations", response_model=List[RecommendationContract])
def list_recommendations(
    status: Optional[str] = None,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR", "WAREHOUSE_MANAGER", "STORE_OWNER"])),
):
    """Returns autonomous AI/ML recommendations with trade-off analysis."""
    return alert_service.get_recommendations(status=status)


class DecisionRequest(BaseModel):
    decision: str = "APPROVE"  # APPROVE or REJECT


@router.post("/recommendations/{rec_id}/decision")
@router.post("/recommendations/{rec_id}/approve")
def approve_recommendation(
    rec_id: str,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR", "WAREHOUSE_MANAGER"])),
):
    """
    Operator approves an autonomous recommendation.
    Executes the underlying intervention (dynamic truck rescue, MILP rebalance, or safety buffer elevation).
    """
    live_engine = get_or_create_live_engine()
    result = alert_service.approve_recommendation(rec_id, live_engine=live_engine)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@router.post("/recommendations/{rec_id}/reject")
def reject_recommendation(
    rec_id: str,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR", "WAREHOUSE_MANAGER"])),
):
    """Operator explicitly rejects a recommendation."""
    live_engine = get_or_create_live_engine()
    result = alert_service.reject_recommendation(rec_id, live_engine=live_engine)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@router.get("/activity", response_model=List[ActivityContract])
def get_activity_log(
    limit: int = 50,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR", "WAREHOUSE_MANAGER", "STORE_OWNER", "TRUCK_DRIVER"])),
):
    """Returns the immutable audit log of simulation events, disruptions, and decisions."""
    return alert_service.activity_log[:limit]
