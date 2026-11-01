"""
backend/tests/test_contracts.py
Validates contract models, seed generation, and network specifications.
"""

from contracts.models import (
    NodeRole,
    ProductContract,
    NodeContract,
    InventoryContract,
    TruckContract,
    KPISnapshotContract,
)
from contracts.seed_specs import (
    generate_seed_products,
    generate_seed_network,
    generate_seed_trucks,
    generate_initial_warehouse_inventories,
)


def test_seed_sizes_match_specification():
    # Exactly 50 products
    products = generate_seed_products(50)
    assert len(products) == 50

    # Exactly 1 Mfr, 2 Dist, 3 WH, 20 Stores
    net = generate_seed_network()
    nodes = net["nodes"]
    assert len(nodes) == 26

    mfrs = [n for n in nodes if n.role == NodeRole.MANUFACTURER]
    dists = [n for n in nodes if n.role == NodeRole.DISTRIBUTOR]
    whs = [n for n in nodes if n.role == NodeRole.WAREHOUSE]
    stores = [n for n in nodes if n.role == NodeRole.STORE]

    assert len(mfrs) == 1
    assert len(dists) == 2
    assert len(whs) == 3
    assert len(stores) == 20

    # Exactly 10 trucks
    trucks = generate_seed_trucks(10)
    assert len(trucks) == 10

    # Inventories for 3 warehouses x 50 products = 150 inventory contracts
    inventories = generate_initial_warehouse_inventories(nodes, products)
    assert len(inventories) == 150


def test_contract_serialization():
    prod = ProductContract(
        id="PROD_TEST",
        sku="SKU-TEST-001",
        name="Test Item",
        category="Beverages",
        unit_cost=10.0,
        unit_price=18.0,
    )
    data = prod.model_dump()
    assert data["sku"] == "SKU-TEST-001"

    prod_restored = ProductContract.model_validate(data)
    assert prod_restored.id == prod.id
