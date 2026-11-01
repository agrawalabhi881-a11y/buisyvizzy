"""
backend/tests/test_phase4_services.py
Integration test suite for Phase 4 Core Backend Services & REST APIs:
- Role-based JWT authentication (5 roles)
- Store order placement & tracking
- Warehouse capacity & fulfillment
- Automated escalation & backorder handling on shortages
- Upstream (s, S) procurement policy evaluation
"""

from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models import Distributor, Inventory, Manufacturer, Order, Product, Store, Warehouse
from app.services.auth_service import DEMO_USERS, create_access_token
from app.services.procurement_service import ProcurementService
from app.services.store_service import StoreService
from app.services.warehouse_service import WarehouseService

client = TestClient(app)


def test_auth_demo_login_and_me():
    res = client.post("/api/auth/login", json={"username": "admin", "password": "adminpassword"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    assert res.json()["role"] == "ADMIN"

    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    assert res_me.json()["username"] == "admin"
    assert res_me.json()["role"] == "ADMIN"

    res_bad = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert res_bad.status_code == 401


def test_store_order_placement_and_tracking(session: Session):
    store = session.query(Store).first()
    product = session.query(Product).first()

    order = StoreService.place_order(
        store_id=store.id,
        lines_input=[{"product_id": product.id, "quantity": 15.0}],
        session=session,
    )

    assert order.id is not None
    assert order.order_number.startswith("ORD-ST")
    assert order.status == "submitted"
    assert len(order.lines) == 1
    assert float(order.lines[0].quantity_requested) == 15.0

    track_res = StoreService.track_order(order.order_number, session)
    assert track_res["order_number"] == order.order_number
    assert track_res["status"] == "submitted"
    assert len(track_res["lines"]) == 1


def test_warehouse_fulfillment_and_stock_deduction(session: Session):
    store = session.query(Store).first()
    product = session.query(Product).first()
    warehouse = session.query(Warehouse).first()

    # Expand warehouse capacity for test
    warehouse.storage_capacity = Decimal("1000.0")
    session.commit()

    inv = session.query(Inventory).filter_by(warehouse_id=warehouse.id, product_id=product.id).first()
    if not inv:
        inv = Inventory(
            warehouse_id=warehouse.id,
            product_id=product.id,
            quantity_on_hand=Decimal("50.0"),
            quantity_reserved=Decimal("0.0"),
            reorder_level=Decimal("20.0"),
            maximum_stock_level=Decimal("100.0"),
        )
        session.add(inv)
    else:
        inv.quantity_on_hand = Decimal("50.0")
    session.commit()

    order = StoreService.place_order(
        store_id=store.id,
        lines_input=[{"product_id": product.id, "quantity": 20.0}],
        session=session,
    )

    result = WarehouseService.fulfill_order(warehouse.id, order.id, session)
    assert result["status"] == "fulfilled"
    assert result["has_shortage"] is False
    assert result["processing_lead_time_hours"] > 0

    session.refresh(inv)
    assert float(inv.quantity_on_hand) == 30.0


def test_warehouse_shortage_escalation_and_backorder(session: Session):
    store = session.query(Store).first()
    product = session.query(Product).first()
    warehouse = session.query(Warehouse).first()

    warehouse.storage_capacity = Decimal("1000.0")
    inv = session.query(Inventory).filter_by(warehouse_id=warehouse.id, product_id=product.id).first()
    if not inv:
        inv = Inventory(
            warehouse_id=warehouse.id,
            product_id=product.id,
            quantity_on_hand=Decimal("5.0"),
            quantity_reserved=Decimal("0.0"),
            reorder_level=Decimal("10.0"),
            maximum_stock_level=Decimal("50.0"),
        )
        session.add(inv)
    else:
        inv.quantity_on_hand = Decimal("5.0")
    session.commit()

    order = StoreService.place_order(
        store_id=store.id,
        lines_input=[{"product_id": product.id, "quantity": 20.0}],
        session=session,
    )

    result = WarehouseService.fulfill_order(warehouse.id, order.id, session)
    assert result["has_shortage"] is True
    assert result["status"] == "partially_fulfilled"
    assert result["lines"][0]["fulfilled"] == 5.0
    assert result["lines"][0]["shortage"] == 15.0

    line = order.lines[0]
    assert line.backorder is not None
    assert float(line.backorder.remaining_quantity) == 15.0

    esc = WarehouseService.escalate_unfulfillable_order(order.id, session)
    assert esc["status"] == "escalated_to_distributor"


def test_procurement_sS_replenishment_evaluation(session: Session):
    distributor = session.query(Distributor).first()
    warehouse = session.query(Warehouse).first()
    product = session.query(Product).first()

    warehouse.storage_capacity = Decimal("1000.0")
    inv = session.query(Inventory).filter_by(warehouse_id=warehouse.id, product_id=product.id).first()
    if not inv:
        inv = Inventory(
            warehouse_id=warehouse.id,
            product_id=product.id,
            quantity_on_hand=Decimal("5.0"),
            quantity_reserved=Decimal("0.0"),
            reorder_level=Decimal("20.0"),
            maximum_stock_level=Decimal("80.0"),
        )
        session.add(inv)
    else:
        inv.quantity_on_hand = Decimal("5.0")
        inv.reorder_level = Decimal("20.0")
        inv.maximum_stock_level = Decimal("80.0")
    session.commit()

    pos = ProcurementService.evaluate_sS_procurement(distributor.id, session)
    assert len(pos) >= 1
    assert pos[0]["warehouse_id"] == warehouse.id
    assert pos[0]["product_id"] == product.id
    assert pos[0]["quantity_ordered"] > 0


def test_unmet_demand_penalty_logging(session: Session):
    store = session.query(Store).first()
    product = session.query(Product).first()

    order = StoreService.place_order(
        store_id=store.id,
        lines_input=[{"product_id": product.id, "quantity": 25.0}],
        session=session,
    )

    record = StoreService.log_unmet_demand(
        order_id=order.id,
        store_id=store.id,
        product_id=product.id,
        requested_quantity=25.0,
        fulfilled_quantity=0.0,
        unmet_quantity=25.0,
        reason="supplier_blackout",
        session=session,
    )
    assert record.id is not None
    assert float(record.unmet_quantity) == 25.0


def test_simulation_api_endpoint_execution():
    admin_token = create_access_token({"sub": "admin", "role": "ADMIN"})
    response = client.post(
        "/api/simulation/run",
        json={
            "seed": 42,
            "duration_ticks": 5,
            "optimizer_enabled": True,
            "demand_spike_severity": 2.5,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["duration_ticks"] == 5
    assert len(data["snapshots"]) == 5
    assert "fill_rate" in data["final_kpis"]
