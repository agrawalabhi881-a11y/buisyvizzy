import os
import sys
import pytest
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def admin_headers():
    """Log in as the demo admin and return authenticated request headers."""
    with TestClient(app) as test_client:
        response = test_client.post(
            "/api/auth/login",
            json={
                "username": "admin",
                "password": "adminpassword",
            },
        )

    assert response.status_code == 200, response.text
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}

# Ensure both backend root and repo root are in sys.path
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
repo_root = os.path.abspath(os.path.join(backend_root, ".."))
for p in [backend_root, repo_root]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.database.base import Base
from app.models import Distributor, Manufacturer, Product, Store, Warehouse


@pytest.fixture
def engine() -> Engine:
    test_engine = create_engine("sqlite:///:memory:")

    @event.listens_for(test_engine, "connect")
    def enable_foreign_keys(connection, _record) -> None:
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(test_engine)
    yield test_engine
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()


@pytest.fixture
def session(engine: Engine):
    with Session(engine) as test_session:
        manufacturer = Manufacturer(name="Test manufacturer", location="Test")
        test_session.add(manufacturer)
        test_session.flush()
        distributor = Distributor(
            name="Test distributor", location="Test", manufacturer=manufacturer
        )
        test_session.add(distributor)
        test_session.flush()
        warehouse = Warehouse(
            name="Test warehouse",
            location="Test",
            latitude=34.05,
            longitude=-118.24,
            storage_capacity=10,
            distributor=distributor,
        )
        test_session.add(warehouse)
        test_session.flush()
        store = Store(
            name="Test store",
            state_id="CA",
            latitude=34.06,
            longitude=-118.25,
            distributor=distributor,
            assigned_warehouse=warehouse,
        )
        product = Product(name="Test product", unit_cost=2.5)
        test_session.add_all([store, product])
        test_session.commit()
        yield test_session
