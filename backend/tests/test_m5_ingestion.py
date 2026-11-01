from __future__ import annotations

from datetime import date

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ingestion.m5 import (
    M5Paths,
    generate_lead_times,
    ingest_m5,
    inspect_and_validate,
    select_m5_product_ids,
    simulate_inventory_history,
)
from app.models import (
    CalendarWeek,
    DailySalesRecord,
    Distributor,
    Inventory,
    M5CalendarDate,
    Manufacturer,
    Product,
    Store,
    Warehouse,
    WeeklySellPrice,
)


def _fixture_files(tmp_path, sales_units=(2, 0)) -> M5Paths:
    raw = tmp_path / "m5"
    raw.mkdir()
    calendar = pd.DataFrame(
        [
            {
                "d": "d_1",
                "date": "2011-01-29",
                "wm_yr_wk": "11101",
                "weekday": "Saturday",
                "wday": 1,
                "month": 1,
                "year": 2011,
                "event_name_1": None,
                "event_type_1": None,
                "event_name_2": None,
                "event_type_2": None,
                "snap_CA": 0,
                "snap_TX": 0,
                "snap_WI": 0,
            },
            {
                "d": "d_2",
                "date": "2011-01-30",
                "wm_yr_wk": "11101",
                "weekday": "Sunday",
                "wday": 2,
                "month": 1,
                "year": 2011,
                "event_name_1": None,
                "event_type_1": None,
                "event_name_2": None,
                "event_type_2": None,
                "snap_CA": 0,
                "snap_TX": 0,
                "snap_WI": 0,
            },
        ]
    )
    calendar.to_csv(raw / "calendar.csv", index=False)
    pd.DataFrame(
        [
            {
                "id": f"FOODS_1_001_{store_id}_validation",
                "item_id": "FOODS_1_001",
                "dept_id": "FOODS_1",
                "cat_id": "FOODS",
                "store_id": store_id,
                "state_id": store_id.split("_")[0],
                "d_1": sales_units[0],
                "d_2": sales_units[1],
            }
            for store_id in (
                "CA_1",
                "CA_2",
                "CA_3",
                "CA_4",
                "TX_1",
                "TX_2",
                "TX_3",
                "WI_1",
                "WI_2",
                "WI_3",
            )
        ]
    ).to_csv(raw / "sales_train_validation.csv", index=False)
    pd.DataFrame(
        [
            {
                "store_id": store_id,
                "item_id": "FOODS_1_001",
                "wm_yr_wk": "11101",
                "sell_price": 1.25,
            }
            for store_id in (
                "CA_1",
                "CA_2",
                "CA_3",
                "CA_4",
                "TX_1",
                "TX_2",
                "TX_3",
                "WI_1",
                "WI_2",
                "WI_3",
            )
        ]
    ).to_csv(raw / "sell_prices.csv", index=False)
    return M5Paths.from_raw_dir(raw)


def _placeholder_network(engine) -> None:
    with Session(engine) as session, session.begin():
        manufacturer = Manufacturer(name="M5 test manufacturer", location="test")
        session.add(manufacturer)
        session.flush()
        distributors = [
            Distributor(
                name=f"M5 test distributor {index}",
                location="test",
                manufacturer_id=manufacturer.id,
            )
            for index in (1, 2)
        ]
        session.add_all(distributors)
        session.flush()
        warehouses = [
            Warehouse(
                name=f"M5 test warehouse {index}",
                location=location,
                latitude=latitude,
                longitude=longitude,
                storage_capacity=100,
                distributor_id=distributors[distributor_index].id,
            )
            for index, (location, latitude, longitude, distributor_index) in enumerate(
                [
                    ("California", 34, -118, 0),
                    ("Texas", 32, -97, 0),
                    ("Wisconsin", 43, -89, 1),
                ],
                start=1,
            )
        ]
        session.add_all(warehouses)
        session.flush()
        session.flush()
        store = Store(
            name="Synthetic Store 001",
            synthetic_code="SYN-STORE-001",
            state_id="CA",
            latitude=34.1,
            longitude=-118.1,
            distributor_id=distributors[0].id,
            assigned_warehouse_id=warehouses[0].id,
        )
        session.add_all([store, Product(name="Synthetic Product 001")])


def test_missing_files_stop_gracefully_and_report(tmp_path) -> None:
    paths = M5Paths.from_raw_dir(tmp_path / "not-present")
    report = inspect_and_validate(paths)
    assert report["status"] == "missing_files"
    assert len(report["missing_files"]) == 3
    assert "Kaggle" in report["download_instructions"]


def test_schema_validation_reports_missing_required_columns(tmp_path) -> None:
    paths = _fixture_files(tmp_path)
    pd.DataFrame([{"wrong": "column"}]).to_csv(paths.calendar, index=False)
    report = inspect_and_validate(paths, enforce_expected_dimensions=False)
    assert report["status"] == "invalid"
    assert any(
        "calendar missing columns" in error for error in report["validation_errors"]
    )


def test_ingestion_maps_dimensions_and_is_idempotent(engine, tmp_path) -> None:
    _placeholder_network(engine)
    paths = _fixture_files(tmp_path)
    report_path = tmp_path / "report.json"

    first = ingest_m5(
        engine, paths, report_path, chunksize=1, enforce_expected_dimensions=False
    )
    second = ingest_m5(
        engine, paths, report_path, chunksize=1, enforce_expected_dimensions=False
    )

    assert first["status"] == second["status"] == "ingested", (
        first.get("database_validation"),
        second.get("database_validation"),
    )
    assert first["mappings"]["selected_products"] == 1
    assert first["mappings"]["selected_store_ids"] == [
        "CA_1",
        "CA_2",
        "CA_3",
        "CA_4",
        "TX_1",
        "TX_2",
        "TX_3",
        "WI_1",
        "WI_2",
        "WI_3",
    ]
    assert first["ingestion"]["sales_inserted"] == 20
    assert second["ingestion"]["sales_inserted"] == 0
    assert second["sales_reconciliation"]["reconciled"] is True
    assert second["sales_reconciliation"]["units_reconciled"] is True
    assert report_path.with_suffix(".md").is_file()
    with Session(engine) as session:
        assert (
            session.scalar(
                select(func.count())
                .select_from(Product)
                .where(Product.m5_item_id == "FOODS_1_001")
            )
            == 1
        )
        assert session.scalar(select(func.count()).select_from(Product)) == 1
        assert session.scalar(select(func.count()).select_from(Store)) == 10
        assert all(
            product.m5_item_id is not None
            for product in session.scalars(select(Product))
        )
        assert all(
            store.m5_store_id is not None for store in session.scalars(select(Store))
        )
        assert session.scalar(select(func.count()).select_from(DailySalesRecord)) == 20
        assert session.scalar(select(func.count()).select_from(M5CalendarDate)) == 2
        assert session.scalar(select(func.count()).select_from(CalendarWeek)) == 1
        assert session.scalar(select(func.count()).select_from(WeeklySellPrice)) == 10
        assert session.scalar(select(func.sum(DailySalesRecord.units_sold))) == 20
        assert (
            session.scalar(
                select(func.count())
                .select_from(DailySalesRecord)
                .where(DailySalesRecord.source_dataset == "m5_forecasting")
            )
            == 20
        )
        mapped_store = session.scalar(select(Store).where(Store.m5_store_id == "CA_1"))
        assert mapped_store is not None and mapped_store.synthetic_code is None
        assert mapped_store.name == "Store 1"
        assert (
            mapped_store.location_source
            == "approximate_state_centroid_not_store_address"
        )
        assert mapped_store.distributor_id == 1
        assert mapped_store.assigned_warehouse_id == 1
        assert session.scalar(select(func.count()).select_from(Inventory)) == 0


def test_invalid_sales_are_reported_without_database_changes(engine, tmp_path) -> None:
    _placeholder_network(engine)
    paths = _fixture_files(tmp_path, sales_units=(-1, 0))
    report = ingest_m5(
        engine, paths, tmp_path / "report.json", enforce_expected_dimensions=False
    )
    assert report["status"] == "invalid"
    assert report["invalid_records"]["sales_values"] == 10
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(DailySalesRecord)) == 0
        assert (
            session.scalar(
                select(func.count())
                .select_from(Product)
                .where(Product.m5_item_id.is_not(None))
            )
            == 0
        )


def test_product_selection_is_deterministic_and_price_coverage_aware(tmp_path) -> None:
    sales_path = tmp_path / "sales.csv"
    prices_path = tmp_path / "prices.csv"
    pd.DataFrame(
        [
            {"item_id": "FOODS_1_001", "dept_id": "FOODS_1"},
            {"item_id": "FOODS_1_002", "dept_id": "FOODS_1"},
            {"item_id": "HOUSEHOLD_1_001", "dept_id": "HOUSEHOLD_1"},
            {"item_id": "HOUSEHOLD_1_002", "dept_id": "HOUSEHOLD_1"},
        ]
    ).to_csv(sales_path, index=False)
    pd.DataFrame(
        [
            {"item_id": "FOODS_1_001", "store_id": "CA_1"},
            {"item_id": "FOODS_1_002", "store_id": "CA_1"},
            {"item_id": "FOODS_1_002", "store_id": "CA_2"},
            {"item_id": "HOUSEHOLD_1_001", "store_id": "WI_1"},
        ]
    ).to_csv(prices_path, index=False)

    selected = select_m5_product_ids(sales_path, limit=2, prices_path=prices_path)
    assert selected == ["FOODS_1_002", "HOUSEHOLD_1_001"]
    assert (
        select_m5_product_ids(sales_path, limit=2, prices_path=prices_path) == selected
    )


def test_inventory_replay_distinguishes_zero_sales_from_potential_stockout() -> None:
    sales = pd.DataFrame(
        [
            {
                "item_id": "item",
                "store_id": "store",
                "date": date(2020, 1, 1),
                "units_sold": 0,
            },
            {
                "item_id": "item",
                "store_id": "store",
                "date": date(2020, 1, 2),
                "units_sold": 8,
            },
        ]
    )
    history = simulate_inventory_history(sales, opening_days=0.1, reorder_days=0)
    assert bool(history.iloc[0]["potential_stockout"]) is False
    assert history.iloc[0]["stockout_classification"] == (
        "observed_zero_sales_no_stockout_evidence"
    )
    assert bool(history.iloc[1]["potential_stockout"]) is True
    assert bool(history.iloc[1]["simulated_confirmed_stockout"]) is True
    assert history.iloc[1]["simulated_unmet_demand_units"] > 0
    assert (history["closing_inventory"] >= 0).all()
    assert history["history_type"].str.contains("synthetic").all()


def test_lead_time_generation_is_positive_and_reproducible() -> None:
    lanes = [{"lane_type": "warehouse_to_store", "origin": "WH1", "destination": "S1"}]
    first = generate_lead_times(lanes, samples_per_lane=20, seed=17)
    second = generate_lead_times(lanes, samples_per_lane=20, seed=17)
    pd.testing.assert_frame_equal(first, second)
    assert (first["lead_time_days"] > 0).all()
    configured = generate_lead_times(
        lanes,
        samples_per_lane=2,
        seed=17,
        lane_parameters={"warehouse_to_store": {"median_days": 2.0, "sigma": 0.4}},
    )
    assert set(configured["median_parameter_days"]) == {2.0}
