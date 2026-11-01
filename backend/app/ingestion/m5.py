from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import sqlite3
import tempfile
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd  # type: ignore[import-untyped]
from sqlalchemy import Engine, delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.models import (
    CalendarWeek,
    DailySalesRecord,
    DisruptionTarget,
    Distributor,
    Inventory,
    M5CalendarDate,
    Manufacturer,
    Order,
    OrderLine,
    Product,
    Shipment,
    Store,
    UnmetDemand,
    Warehouse,
    WeeklySellPrice,
)

DATASET_NAME = "m5_forecasting"
SALES_FILE = "sales_train_validation.csv"
CALENDAR_FILE = "calendar.csv"
PRICES_FILE = "sell_prices.csv"
EVALUATION_FILE = "sales_train_evaluation.csv"
SAMPLE_SUBMISSION_FILE = "sample_submission.csv"
M5_STORE_IDS = (
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
STORE_LABELS = {
    store_id: f"Store {index}" for index, store_id in enumerate(M5_STORE_IDS, start=1)
}
STORE_DISTRIBUTOR_INDEX = {
    "CA_1": 0,
    "CA_2": 0,
    "CA_3": 0,
    "CA_4": 0,
    "TX_1": 0,
    "TX_2": 1,
    "TX_3": 1,
    "WI_1": 1,
    "WI_2": 1,
    "WI_3": 1,
}
STATE_CENTROID_APPROXIMATIONS = {
    "CA": (36.8, -119.4),
    "TX": (31.0, -99.9),
    "WI": (44.5, -89.5),
}
STATE_NAMES = {"CA": "california", "TX": "texas", "WI": "wisconsin"}
SALES_METADATA_COLUMNS = [
    "id",
    "item_id",
    "dept_id",
    "cat_id",
    "store_id",
    "state_id",
]
REQUIRED_CALENDAR_COLUMNS = {
    "d",
    "date",
    "wm_yr_wk",
    "weekday",
    "wday",
    "month",
    "year",
    "event_name_1",
    "event_type_1",
    "event_name_2",
    "event_type_2",
    "snap_CA",
    "snap_TX",
    "snap_WI",
}
REQUIRED_PRICE_COLUMNS = {"store_id", "item_id", "wm_yr_wk", "sell_price"}
INSERT_BATCH_SIZE = 100_000


@dataclass(frozen=True)
class M5Paths:
    raw_dir: Path
    sales: Path
    calendar: Path
    prices: Path
    evaluation: Path | None = None
    sample_submission: Path | None = None

    @classmethod
    def from_raw_dir(cls, raw_dir: Path) -> M5Paths:
        def locate(filename: str) -> Path:
            direct = raw_dir / filename
            if direct.is_file():
                return direct
            matches = list(raw_dir.rglob(filename)) if raw_dir.is_dir() else []
            return matches[0] if len(matches) == 1 else direct

        def locate_optional(filename: str) -> Path | None:
            direct = raw_dir / filename
            if direct.is_file():
                return direct
            matches = list(raw_dir.rglob(filename)) if raw_dir.is_dir() else []
            return matches[0] if len(matches) == 1 else None

        return cls(
            raw_dir=raw_dir,
            sales=locate(SALES_FILE),
            calendar=locate(CALENDAR_FILE),
            prices=locate(PRICES_FILE),
            evaluation=locate_optional(EVALUATION_FILE),
            sample_submission=locate_optional(SAMPLE_SUBMISSION_FILE),
        )

    def missing(self) -> list[Path]:
        return [
            path
            for path in (self.sales, self.calendar, self.prices)
            if not path.is_file()
        ]


def _nullable(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, np.generic):
        return value.item()
    return value


def _raw_file_fingerprints(paths: M5Paths) -> dict[str, dict[str, Any]]:
    candidates = {
        SALES_FILE: paths.sales,
        CALENDAR_FILE: paths.calendar,
        PRICES_FILE: paths.prices,
        EVALUATION_FILE: paths.evaluation,
        SAMPLE_SUBMISSION_FILE: paths.sample_submission,
    }
    fingerprints: dict[str, dict[str, Any]] = {}
    for filename, path in candidates.items():
        if path is None or not path.is_file():
            continue
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
                digest.update(block)
        fingerprints[filename] = {
            "bytes": path.stat().st_size,
            "sha256": digest.hexdigest(),
        }
    return fingerprints


def _insert_ignore(
    connection: Any, model: type[Any], rows: list[dict[str, Any]], keys: list[str]
) -> int:
    if not rows:
        return 0
    dialect = connection.dialect.name
    if dialect == "postgresql":
        result = connection.execute(
            pg_insert(model).values(rows).on_conflict_do_nothing(index_elements=keys)
        )
    elif dialect == "sqlite":
        result = connection.execute(
            sqlite_insert(model)
            .values(rows)
            .on_conflict_do_nothing(index_elements=keys)
        )
    else:
        raise RuntimeError(f"Bulk idempotent ingestion is unsupported for {dialect}")
    return max(result.rowcount or 0, 0)


def _postgres_copy_batch(
    connection: Any,
    stage_table: str,
    target_table: str,
    columns: list[str],
    rows: list[dict[str, Any]],
    conflict_columns: list[str],
) -> int:
    """Load a batch with PostgreSQL COPY, then merge through target constraints."""
    column_sql = ", ".join(columns)
    conflict_sql = ", ".join(conflict_columns)
    raw_connection = connection.connection.driver_connection
    with connection.begin():
        with raw_connection.cursor().copy(
            f"COPY {stage_table} ({column_sql}) FROM STDIN"
        ) as copy:
            for row in rows:
                copy.write_row(
                    tuple(
                        (
                            row[column].item()
                            if isinstance(row[column], np.generic)
                            else row[column]
                        )
                        for column in columns
                    )
                )
        result = connection.exec_driver_sql(
            f"INSERT INTO {target_table} ({column_sql}) "
            f"SELECT {column_sql} FROM {stage_table} "
            f"ON CONFLICT ({conflict_sql}) DO NOTHING"
        )
        connection.exec_driver_sql(f"TRUNCATE {stage_table}")
        return max(result.rowcount or 0, 0)


def _upsert(
    connection: Any,
    model: type[Any],
    rows: list[dict[str, Any]],
    keys: list[str],
    update: list[str],
) -> int:
    if not rows:
        return 0
    dialect = connection.dialect.name
    factory = (
        pg_insert
        if dialect == "postgresql"
        else sqlite_insert if dialect == "sqlite" else None
    )
    if factory is None:
        raise RuntimeError(f"Bulk upsert is unsupported for {dialect}")
    statement = factory(model).values(rows)
    statement = statement.on_conflict_do_update(
        index_elements=keys,
        set_={column: getattr(statement.excluded, column) for column in update},
    )
    return max(connection.execute(statement).rowcount or 0, 0)


def inspect_and_validate(
    paths: M5Paths, chunk_rows: int = 128, enforce_expected_dimensions: bool = True
) -> dict[str, Any]:
    """Inspect all M5 inputs before any database writes; invalid data is reported, not dropped."""
    missing = paths.missing()
    report: dict[str, Any] = {
        "dataset": DATASET_NAME,
        "status": "missing_files" if missing else "validating",
        "source_files": {},
        "validation_errors": [],
        "missing_values": {},
        "duplicate_records": {},
        "invalid_records": {},
        "mappings": {},
        "ingestion": {"records_inserted": 0, "records_skipped_as_existing": 0},
    }
    if missing:
        report["missing_files"] = [str(path) for path in missing]
        report["download_instructions"] = (
            "Download the M5 Forecasting Accuracy competition files from Kaggle and place "
            f"{SALES_FILE}, {CALENDAR_FILE}, and {PRICES_FILE} in {paths.raw_dir}. "
            "The pipeline does not create or substitute M5 records."
        )
        return report

    calendar = pd.read_csv(paths.calendar)
    report["source_files"][CALENDAR_FILE] = {
        "rows": len(calendar),
        "columns": len(calendar.columns),
        "column_names": list(calendar.columns),
    }
    missing_calendar_columns = sorted(REQUIRED_CALENDAR_COLUMNS - set(calendar.columns))
    if missing_calendar_columns:
        report["validation_errors"].append(
            f"calendar missing columns: {missing_calendar_columns}"
        )
    if not missing_calendar_columns:
        report["missing_values"][CALENDAR_FILE] = {
            column: int(count)
            for column, count in calendar.isna().sum().items()
            if count
        }
        date_values = pd.to_datetime(calendar["date"], errors="coerce")
        invalid_calendar = int(date_values.isna().sum())
        if invalid_calendar:
            report["invalid_records"]["calendar_dates"] = invalid_calendar
            report["validation_errors"].append("calendar contains invalid dates")
        duplicate_calendar = int(
            calendar.duplicated(subset=["d"]).sum()
            + calendar.duplicated(subset=["date"]).sum()
        )
        if not date_values.is_monotonic_increasing:
            report["validation_errors"].append("calendar dates are not ordered")
        report["duplicate_records"][CALENDAR_FILE] = duplicate_calendar
        if duplicate_calendar:
            report["validation_errors"].append(
                "calendar contains duplicate day IDs or dates"
            )
    valid_dates = set(calendar["d"].dropna().astype(str)) if "d" in calendar else set()

    sales_header = pd.read_csv(paths.sales, nrows=0).columns.tolist()
    day_columns = [column for column in sales_header if column.startswith("d_")]
    product_ids: set[str] = set()
    store_ids: set[str] = set()
    absent_metadata = sorted(set(SALES_METADATA_COLUMNS) - set(sales_header))
    if absent_metadata or not day_columns:
        report["validation_errors"].append(
            f"sales schema missing metadata {absent_metadata} or d_ daily columns"
        )
    else:
        item_store_pairs: set[tuple[str, str]] = set()
        source_ids: set[str] = set()
        product_metadata: dict[str, tuple[str, str]] = {}
        store_states: dict[str, str] = {}
        source_rows = 0
        bad_sales = 0
        sales_units_total = 0
        missing_sales: Counter[str] = Counter()
        duplicate_sales = 0
        for chunk in pd.read_csv(paths.sales, chunksize=chunk_rows):
            source_rows += len(chunk)
            missing_sales.update(
                {
                    column: int(count)
                    for column, count in chunk[SALES_METADATA_COLUMNS + day_columns]
                    .isna()
                    .sum()
                    .items()
                    if count
                }
            )
            product_ids.update(chunk["item_id"].dropna().astype(str))
            store_ids.update(chunk["store_id"].dropna().astype(str))
            for item_id, dept_id, cat_id in (
                chunk[["item_id", "dept_id", "cat_id"]]
                .drop_duplicates()
                .itertuples(index=False, name=None)
            ):
                key = str(item_id)
                value = (str(dept_id), str(cat_id))
                if key in product_metadata and product_metadata[key] != value:
                    report["validation_errors"].append(
                        f"M5 product {key} maps to multiple departments/categories"
                    )
                product_metadata[key] = value
            for store_id, state_id in (
                chunk[["store_id", "state_id"]]
                .drop_duplicates()
                .itertuples(index=False, name=None)
            ):
                store_key, store_value = str(store_id), str(state_id)
                if store_key in store_states and store_states[store_key] != store_value:
                    report["validation_errors"].append(
                        f"M5 store {store_key} maps to multiple states"
                    )
                store_states[store_key] = store_value
            for row in chunk[["id", "item_id", "store_id"]].itertuples(
                index=False, name=None
            ):
                row_id, item_id, store_id = map(str, row)
                if row_id in source_ids or (item_id, store_id) in item_store_pairs:
                    duplicate_sales += 1
                source_ids.add(row_id)
                item_store_pairs.add((item_id, store_id))
            numeric = chunk[day_columns].apply(pd.to_numeric, errors="coerce")
            bad_sales += int(
                (numeric.isna() | (numeric < 0) | (numeric % 1 != 0)).sum().sum()
            )
            sales_units_total += int(numeric.sum().sum())
        report["source_files"][SALES_FILE] = {
            "rows": source_rows,
            "columns": len(sales_header),
            "column_names": sales_header,
            "product_store_series": len(item_store_pairs),
            "daily_columns": len(day_columns),
        }
        report["missing_values"][SALES_FILE] = dict(missing_sales)
        report["duplicate_records"][SALES_FILE] = duplicate_sales
        report["invalid_records"]["sales_values"] = bad_sales
        report["source_sales_units_total"] = sales_units_total
        report["mappings"]["products_in_source"] = len(product_ids)
        report["mappings"]["stores_in_source"] = len(store_ids)
        report["mappings"]["sales_day_columns_not_in_calendar"] = sorted(
            set(day_columns) - valid_dates
        )
        if product_ids and any(
            not (len(item_id.split("_")) == 3 and item_id.split("_")[1].isdigit())
            for item_id in product_ids
        ):
            report["validation_errors"].append(
                "sales contains malformed M5 item identifiers"
            )
        invalid_stores = sorted(set(store_ids) - set(M5_STORE_IDS))
        store_state_mismatches = sorted(
            store_id
            for store_id, state_id in store_states.items()
            if store_id.split("_")[0] != state_id
        )
        report["mappings"]["invalid_store_ids"] = invalid_stores
        report["mappings"]["store_state_mismatches"] = store_state_mismatches
        if (
            missing_sales
            or duplicate_sales
            or bad_sales
            or set(day_columns) - valid_dates
            or invalid_stores
            or store_state_mismatches
        ):
            report["validation_errors"].append(
                "sales file contains missing/duplicate/invalid values or unmapped days"
            )

    price_header = pd.read_csv(paths.prices, nrows=0).columns.tolist()
    absent_price = sorted(REQUIRED_PRICE_COLUMNS - set(price_header))
    if absent_price:
        report["validation_errors"].append(
            f"sell_prices missing columns: {absent_price}"
        )
    else:
        price_rows = 0
        bad_prices = 0
        missing_prices: Counter[str] = Counter()
        duplicates = 0
        unmapped_prices = 0
        calendar_weeks = (
            set(calendar["wm_yr_wk"].dropna().astype(str))
            if "wm_yr_wk" in calendar
            else set()
        )
        with tempfile.TemporaryDirectory(prefix="m5-price-validation-") as temp_dir:
            dedupe_db = sqlite3.connect(Path(temp_dir) / "price-keys.sqlite")
            dedupe_db.execute(
                "CREATE TABLE price_keys (store_id TEXT, item_id TEXT, week_id TEXT, "
                "PRIMARY KEY (store_id, item_id, week_id)) WITHOUT ROWID"
            )
            try:
                for chunk in pd.read_csv(paths.prices, chunksize=100_000):
                    price_rows += len(chunk)
                    missing_prices.update(
                        {
                            column: int(count)
                            for column, count in chunk.isna().sum().items()
                            if count
                        }
                    )
                    price_values = pd.to_numeric(chunk["sell_price"], errors="coerce")
                    bad_prices += int((price_values.isna() | (price_values < 0)).sum())
                    keys = [
                        tuple(map(str, key))
                        for key in chunk[
                            ["store_id", "item_id", "wm_yr_wk"]
                        ].itertuples(index=False, name=None)
                    ]
                    before = dedupe_db.total_changes
                    dedupe_db.executemany(
                        "INSERT OR IGNORE INTO price_keys VALUES (?, ?, ?)", keys
                    )
                    duplicates += len(keys) - (dedupe_db.total_changes - before)
                    for store_id, item_id, week_id in keys:
                        if (
                            store_id not in store_ids
                            or item_id not in product_ids
                            or week_id not in calendar_weeks
                        ):
                            unmapped_prices += 1
                    dedupe_db.commit()
            finally:
                dedupe_db.close()
        report["source_files"][PRICES_FILE] = {
            "rows": price_rows,
            "columns": len(price_header),
            "column_names": price_header,
        }
        report["missing_values"][PRICES_FILE] = dict(missing_prices)
        report["duplicate_records"][PRICES_FILE] = duplicates
        report["invalid_records"]["selling_prices"] = bad_prices
        report["mappings"]["price_rows_with_unmapped_references"] = unmapped_prices
        if missing_prices or duplicates or bad_prices or unmapped_prices:
            report["validation_errors"].append(
                "sell_prices contains missing, duplicate, negative prices, or unmapped references"
            )

    if enforce_expected_dimensions and not absent_metadata and len(product_ids) != 3049:
        report["validation_errors"].append(
            f"expected 3049 M5 products, found {len(product_ids)}"
        )
    if enforce_expected_dimensions and not absent_metadata and len(store_ids) != 10:
        report["validation_errors"].append(
            f"expected 10 M5 stores, found {len(store_ids)}"
        )
    if enforce_expected_dimensions and set(store_ids) != set(M5_STORE_IDS):
        report["validation_errors"].append(
            "sales file must contain the 10 official M5 store identifiers"
        )

    if paths.evaluation is not None and paths.evaluation.is_file():
        evaluation_header = pd.read_csv(paths.evaluation, nrows=0).columns.tolist()
        evaluation_days = [
            column for column in evaluation_header if column.startswith("d_")
        ]
        evaluation_missing_columns = sorted(
            set(SALES_METADATA_COLUMNS) - set(evaluation_header)
        )
        evaluation_rows = 0
        evaluation_bad_values = 0
        evaluation_missing_values: Counter[str] = Counter()
        evaluation_pairs: set[tuple[str, str]] = set()
        evaluation_duplicates = 0
        if evaluation_missing_columns or not evaluation_days:
            report["validation_errors"].append(
                "evaluation sales schema is missing metadata or daily columns"
            )
        else:
            for chunk in pd.read_csv(paths.evaluation, chunksize=chunk_rows):
                evaluation_rows += len(chunk)
                evaluation_missing_values.update(
                    {
                        column: int(count)
                        for column, count in chunk[
                            SALES_METADATA_COLUMNS + evaluation_days
                        ]
                        .isna()
                        .sum()
                        .items()
                        if count
                    }
                )
                numeric = chunk[evaluation_days].apply(pd.to_numeric, errors="coerce")
                evaluation_bad_values += int(
                    (numeric.isna() | (numeric < 0) | (numeric % 1 != 0)).sum().sum()
                )
                for item_id, store_id in chunk[["item_id", "store_id"]].itertuples(
                    index=False, name=None
                ):
                    pair = (str(item_id), str(store_id))
                    if pair in evaluation_pairs:
                        evaluation_duplicates += 1
                    evaluation_pairs.add(pair)
            unmapped_evaluation_days = sorted(set(evaluation_days) - valid_dates)
            missing_evaluation_pairs = (
                sorted(evaluation_pairs - item_store_pairs)
                if "item_store_pairs" in locals()
                else []
            )
            report["source_files"][EVALUATION_FILE] = {
                "rows": evaluation_rows,
                "columns": len(evaluation_header),
                "column_names": evaluation_header,
                "product_store_series": len(evaluation_pairs),
                "daily_columns": len(evaluation_days),
            }
            report["missing_values"][EVALUATION_FILE] = dict(evaluation_missing_values)
            report["duplicate_records"][EVALUATION_FILE] = evaluation_duplicates
            report["invalid_records"][EVALUATION_FILE] = evaluation_bad_values
            report["mappings"][
                "evaluation_days_not_in_calendar"
            ] = unmapped_evaluation_days
            if (
                evaluation_missing_values
                or evaluation_duplicates
                or evaluation_bad_values
                or unmapped_evaluation_days
                or missing_evaluation_pairs
            ):
                report["validation_errors"].append(
                    "evaluation sales has invalid values, duplicate/missing series, or unmapped days"
                )

    if paths.sample_submission is not None and paths.sample_submission.is_file():
        submission_header = pd.read_csv(
            paths.sample_submission, nrows=0
        ).columns.tolist()
        forecast_columns = [f"F{index}" for index in range(1, 29)]
        missing_submission_columns = sorted(
            {"id", *forecast_columns} - set(submission_header)
        )
        submission_rows = 0
        submission_missing_ids = 0
        submission_duplicates = 0
        submission_bad_values = 0
        submission_unmapped_ids = 0
        submission_ids: set[str] = set()
        if missing_submission_columns:
            report["validation_errors"].append(
                f"sample submission missing columns: {missing_submission_columns}"
            )
        else:
            for chunk in pd.read_csv(paths.sample_submission, chunksize=100_000):
                submission_rows += len(chunk)
                submission_missing_ids += int(chunk["id"].isna().sum())
                forecast_values = chunk[forecast_columns].apply(
                    pd.to_numeric, errors="coerce"
                )
                submission_bad_values += int(
                    (forecast_values.isna() | (forecast_values < 0)).sum().sum()
                )
                for identifier in chunk["id"].dropna().astype(str):
                    if identifier in submission_ids:
                        submission_duplicates += 1
                    submission_ids.add(identifier)
                    parts = identifier.rsplit("_", 3)
                    if (
                        len(parts) != 4
                        or parts[0] not in product_ids
                        or f"{parts[1]}_{parts[2]}" not in store_ids
                        or parts[3] not in {"validation", "evaluation"}
                    ):
                        submission_unmapped_ids += 1
            report["source_files"][SAMPLE_SUBMISSION_FILE] = {
                "rows": submission_rows,
                "columns": len(submission_header),
                "column_names": submission_header,
                "expected_rows_for_validation_and_evaluation": 2
                * int(report["source_files"].get(SALES_FILE, {}).get("rows", 0)),
            }
            report["missing_values"][SAMPLE_SUBMISSION_FILE] = (
                {"id": submission_missing_ids} if submission_missing_ids else {}
            )
            report["duplicate_records"][SAMPLE_SUBMISSION_FILE] = submission_duplicates
            report["invalid_records"][SAMPLE_SUBMISSION_FILE] = {
                "forecast_values": submission_bad_values,
                "unmapped_series_identifiers": submission_unmapped_ids,
            }
            if (
                submission_missing_ids
                or submission_duplicates
                or submission_bad_values
                or submission_unmapped_ids
                or submission_rows
                != 2 * int(report["source_files"].get(SALES_FILE, {}).get("rows", 0))
            ):
                report["validation_errors"].append(
                    "sample submission has missing, duplicate, invalid, or unmapped values"
                )
    report["raw_file_fingerprints_before_ingestion"] = _raw_file_fingerprints(paths)
    report["status"] = "invalid" if report["validation_errors"] else "validated"
    report["rejected_records"] = {
        "calendar_rows": int(report.get("invalid_records", {}).get("calendar_dates", 0))
        + int(report.get("duplicate_records", {}).get(CALENDAR_FILE, 0)),
        "sales_rows_or_values": int(
            report.get("invalid_records", {}).get("sales_values", 0)
        )
        + int(report.get("duplicate_records", {}).get(SALES_FILE, 0)),
        "price_rows": int(report.get("invalid_records", {}).get("selling_prices", 0))
        + int(report.get("duplicate_records", {}).get(PRICES_FILE, 0))
        + int(report.get("mappings", {}).get("price_rows_with_unmapped_references", 0)),
    }
    report["checks"] = {
        "required_files_present": not bool(paths.missing()),
        "source_data_valid": report["status"] == "validated",
        "validation_errors": len(report["validation_errors"]),
    }
    return report


def _calendar_rows(
    calendar: pd.DataFrame,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    weeks = [
        {"wm_yr_wk": str(value)}
        for value in calendar["wm_yr_wk"].dropna().astype(str).unique()
    ]
    dates: list[dict[str, Any]] = []
    for row in calendar.to_dict(orient="records"):
        parsed = pd.to_datetime(row["date"], errors="raise").date()
        dates.append(
            {
                "d": str(row["d"]),
                "date": parsed,
                "wm_yr_wk": str(row["wm_yr_wk"]),
                "weekday": str(row["weekday"]),
                "wday": int(row["wday"]),
                "month": int(row["month"]),
                "year": int(row["year"]),
                "event_name_1": _nullable(row.get("event_name_1")),
                "event_type_1": _nullable(row.get("event_type_1")),
                "event_name_2": _nullable(row.get("event_name_2")),
                "event_type_2": _nullable(row.get("event_type_2")),
                "snap_CA": (
                    bool(row.get("snap_CA", 0))
                    if not pd.isna(row.get("snap_CA", 0))
                    else False
                ),
                "snap_TX": (
                    bool(row.get("snap_TX", 0))
                    if not pd.isna(row.get("snap_TX", 0))
                    else False
                ),
                "snap_WI": (
                    bool(row.get("snap_WI", 0))
                    if not pd.isna(row.get("snap_WI", 0))
                    else False
                ),
            }
        )
    return weeks, dates


def _map_stores(session: Session, sales_metadata: pd.DataFrame) -> dict[str, int]:
    pairs = sales_metadata[["store_id", "state_id"]].drop_duplicates()
    if pairs["store_id"].duplicated().any():
        raise ValueError("An M5 store_id maps to multiple states")
    if set(pairs["store_id"].astype(str)) != set(M5_STORE_IDS):
        raise ValueError("M5 input must contain exactly the 10 official store IDs")
    existing = {
        store.m5_store_id: store
        for store in session.scalars(select(Store))
        if store.m5_store_id
    }
    distributors = list(session.scalars(select(Distributor).order_by(Distributor.id)))
    if len(distributors) < 2:
        raise ValueError("Two existing distributors are required to map M5 stores")
    warehouses = list(session.scalars(select(Warehouse).order_by(Warehouse.id)))
    warehouses_by_distributor: dict[int, list[Warehouse]] = {}
    for warehouse in warehouses:
        warehouses_by_distributor.setdefault(warehouse.distributor_id, []).append(
            warehouse
        )
    if any(
        not warehouses_by_distributor.get(distributor.id)
        for distributor in distributors[:2]
    ):
        raise ValueError("Each distributor must own at least one warehouse")
    for row in pairs.itertuples(index=False):
        external_id, state_id = str(row.store_id), str(row.state_id)
        if external_id not in STORE_LABELS:
            raise ValueError(f"Unexpected M5 store identifier: {external_id}")
        distributor = distributors[STORE_DISTRIBUTOR_INDEX[external_id]]
        owned_warehouses = warehouses_by_distributor.get(distributor.id, [])
        state_warehouse = next(
            (
                w
                for w in owned_warehouses
                if w.location.lower() == STATE_NAMES.get(state_id, state_id.lower())
            ),
            None,
        )
        warehouse = state_warehouse or owned_warehouses[0]
        store = existing.get(external_id)
        if store is None:
            store = Store(
                m5_store_id=external_id,
                synthetic_code=None,
                state_id=state_id,
                name=STORE_LABELS[external_id],
                distributor_id=distributor.id,
                assigned_warehouse_id=warehouse.id,
                latitude=STATE_CENTROID_APPROXIMATIONS.get(state_id, (39.8, -98.6))[0],
                longitude=STATE_CENTROID_APPROXIMATIONS.get(state_id, (39.8, -98.6))[1],
                location_source="approximate_state_centroid_not_store_address",
            )
            session.add(store)
            existing[external_id] = store
        else:
            if store.distributor_id != distributor.id:
                has_orders = session.scalar(
                    select(func.count())
                    .select_from(Order)
                    .where(Order.source_store_id == store.id)
                )
                if has_orders:
                    raise ValueError(
                        f"Cannot reassign {external_id}; existing store orders depend on its distributor"
                    )
            store.state_id = state_id
            store.name = STORE_LABELS[external_id]
            store.distributor_id = distributor.id
            store.assigned_warehouse_id = warehouse.id
            store.latitude, store.longitude = STATE_CENTROID_APPROXIMATIONS.get(
                state_id, (39.8, -98.6)
            )
            store.location_source = "approximate_state_centroid_not_store_address"
    session.flush()
    return {
        store.m5_store_id: store.id for store in existing.values() if store.m5_store_id
    }


def _prune_non_m5_stores(connection: Any, keep_store_ids: set[int]) -> int:
    stale_ids = list(
        connection.scalars(
            select(Store.id).where(
                Store.m5_store_id.is_(None), Store.id.not_in(keep_store_ids)
            )
        )
    )
    if not stale_ids:
        return 0
    stale_inventory = list(
        connection.execute(
            select(Inventory.quantity_on_hand, Inventory.quantity_reserved).where(
                Inventory.store_id.in_(stale_ids)
            )
        )
    )
    if any(on_hand != 0 or reserved != 0 for on_hand, reserved in stale_inventory):
        raise ValueError("Refusing to remove synthetic stores with nonzero inventory")
    reference_checks = (
        (Order, Order.source_store_id),
        (Shipment, Shipment.destination_store_id),
        (UnmetDemand, UnmetDemand.store_id),
        (DisruptionTarget, DisruptionTarget.store_id),
    )
    for model, column in reference_checks:
        references = connection.scalar(
            select(func.count()).select_from(model).where(column.in_(stale_ids))
        )
        if references:
            raise ValueError(
                f"Refusing to remove synthetic stores: {references} dependent {model.__tablename__} records exist"
            )
    connection.execute(delete(Inventory).where(Inventory.store_id.in_(stale_ids)))
    connection.execute(delete(Store).where(Store.id.in_(stale_ids)))
    return len(stale_ids)


def _prune_non_selected_products(
    connection: Any, selected_item_ids: set[str]
) -> dict[str, int]:
    stale_product_ids = list(
        connection.scalars(
            select(Product.id).where(
                Product.m5_item_id.is_(None)
                | Product.m5_item_id.not_in(selected_item_ids)
            )
        )
    )
    if not stale_product_ids:
        return {
            "products_removed": 0,
            "inventory_records_removed": 0,
            "sales_removed": 0,
            "prices_removed": 0,
        }
    for model, column in (
        (OrderLine, OrderLine.product_id),
        (UnmetDemand, UnmetDemand.product_id),
    ):
        references = connection.scalar(
            select(func.count()).select_from(model).where(column.in_(stale_product_ids))
        )
        if references:
            raise ValueError(
                f"Refusing to remove obsolete products: {references} dependent {model.__tablename__} records exist"
            )
    stale_inventory = list(
        connection.execute(
            select(Inventory.quantity_on_hand, Inventory.quantity_reserved).where(
                Inventory.product_id.in_(stale_product_ids)
            )
        )
    )
    if any(on_hand != 0 or reserved != 0 for on_hand, reserved in stale_inventory):
        raise ValueError("Refusing to remove obsolete products with nonzero inventory")
    # Their M5 sales and prices are outside this requested development subset.
    sales_removed = (
        connection.execute(
            delete(DailySalesRecord).where(
                DailySalesRecord.product_id.in_(stale_product_ids)
            )
        ).rowcount
        or 0
    )
    prices_removed = (
        connection.execute(
            delete(WeeklySellPrice).where(
                WeeklySellPrice.product_id.in_(stale_product_ids)
            )
        ).rowcount
        or 0
    )
    connection.execute(
        delete(Inventory).where(Inventory.product_id.in_(stale_product_ids))
    )
    connection.execute(delete(Product).where(Product.id.in_(stale_product_ids)))
    return {
        "products_removed": len(stale_product_ids),
        "inventory_records_removed": len(stale_inventory),
        "sales_removed": sales_removed,
        "prices_removed": prices_removed,
    }


def reconcile_database_to_m5_subset(
    connection: Any,
    selected_item_ids: set[str],
    selected_store_ids: set[str],
    require_fixed_size: bool = True,
) -> dict[str, int]:
    """Keep exactly the chosen original M5 stores and products, refusing lossy deletes."""
    if (
        require_fixed_size and len(selected_item_ids) != 50
    ) or selected_store_ids != set(M5_STORE_IDS):
        raise ValueError(
            "The development catalog must contain 50 products and 10 M5 stores"
        )
    store_internal_ids = set(
        connection.scalars(
            select(Store.id).where(Store.m5_store_id.in_(selected_store_ids))
        )
    )
    stores_removed = _prune_non_m5_stores(connection, store_internal_ids)
    product_cleanup = _prune_non_selected_products(connection, selected_item_ids)
    actual_store_ids = set(
        connection.scalars(
            select(Store.m5_store_id).where(Store.m5_store_id.is_not(None))
        )
    )
    actual_item_ids = set(
        connection.scalars(
            select(Product.m5_item_id).where(Product.m5_item_id.is_not(None))
        )
    )
    if actual_store_ids != selected_store_ids:
        raise ValueError(
            "Database store catalog does not exactly match the 10 selected M5 stores"
        )
    if actual_item_ids != selected_item_ids:
        raise ValueError(
            "Database product catalog does not exactly match the 50 selected M5 products"
        )
    return {
        "stores_removed": stores_removed,
        **product_cleanup,
    }


def _upsert_products(
    connection: Any, sales_path: Path, selected_item_ids: set[str]
) -> int:
    metadata = pd.read_csv(sales_path, usecols=SALES_METADATA_COLUMNS)
    metadata = metadata[metadata["item_id"].astype(str).isin(selected_item_ids)]
    products = metadata[["item_id", "dept_id", "cat_id"]].drop_duplicates()
    products = products.sort_values("item_id")
    rows = [
        {
            "item_id": str(row.item_id),
            "dept_id": str(row.dept_id),
            "cat_id": str(row.cat_id),
            "name": str(row.item_id),
            "unit_of_measure": "unit",
            "unit_cost": 0,
        }
        for row in products.itertuples(index=False)
    ]
    return _upsert(
        connection, Product, rows, ["item_id"], ["dept_id", "cat_id", "name"]
    )


def select_m5_product_ids(
    sales_path: Path, limit: int = 50, prices_path: Path | None = None
) -> list[str]:
    """Select price-rich, department-balanced genuine M5 IDs deterministically."""
    if limit < 1:
        raise ValueError("product limit must be positive")
    metadata = pd.read_csv(sales_path, usecols=["item_id", "dept_id"]).drop_duplicates(
        "item_id"
    )
    price_coverage: Counter[str] = Counter()
    if prices_path is not None and prices_path.is_file():
        for chunk in pd.read_csv(
            prices_path, usecols=["item_id", "store_id"], chunksize=100_000
        ):
            price_coverage.update(chunk["item_id"].astype(str).value_counts().to_dict())
    by_department: dict[str, list[str]] = {}
    for item_id, department_id in metadata.itertuples(index=False, name=None):
        by_department.setdefault(str(department_id), []).append(str(item_id))
    for item_ids in by_department.values():
        item_ids.sort(key=lambda item_id: (-price_coverage[item_id], item_id))
    positions = dict.fromkeys(by_department, 0)
    selected: list[str] = []
    while len(selected) < limit:
        added = False
        for department_id in sorted(by_department):
            position = positions[department_id]
            if position < len(by_department[department_id]):
                selected.append(by_department[department_id][position])
                positions[department_id] += 1
                added = True
                if len(selected) == limit:
                    break
        if not added:
            break
    return selected


def ingest_m5(
    engine: Engine,
    paths: M5Paths,
    report_path: Path,
    chunksize: int = 64,
    enforce_expected_dimensions: bool = True,
    product_limit: int = 50,
) -> dict[str, Any]:
    pipeline_started = time.perf_counter()
    report = inspect_and_validate(
        paths,
        chunk_rows=chunksize,
        enforce_expected_dimensions=enforce_expected_dimensions,
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    if report["status"] != "validated":
        report["pipeline_execution_seconds"] = round(
            time.perf_counter() - pipeline_started, 3
        )
        write_quality_report(report, report_path)
        return report

    selected_item_ids = select_m5_product_ids(paths.sales, product_limit, paths.prices)
    source_metadata = pd.read_csv(paths.sales, usecols=["item_id", "store_id"])
    selected_series_count = int(
        source_metadata["item_id"].astype(str).isin(selected_item_ids).sum()
    )
    selected_store_ids = sorted(
        source_metadata.loc[
            source_metadata["item_id"].astype(str).isin(selected_item_ids), "store_id"
        ]
        .astype(str)
        .unique()
    )
    if set(selected_store_ids) != set(M5_STORE_IDS):
        raise ValueError(
            "Selected M5 series do not cover exactly the 10 official stores"
        )
    if selected_series_count != len(selected_item_ids) * len(selected_store_ids):
        raise ValueError(
            "Selected M5 products do not have a complete store series mapping"
        )
    report["mappings"].update(
        {
            "selected_products": len(selected_item_ids),
            "selected_item_ids": selected_item_ids,
            "selected_store_ids": selected_store_ids,
            "store_display_labels": {
                store_id: STORE_LABELS[store_id] for store_id in selected_store_ids
            },
            "selected_product_store_series": selected_series_count,
            "selection_method": "deterministic round-robin across departments; products with more valid store-week prices rank first within each department",
        }
    )

    calendar = pd.read_csv(paths.calendar)
    week_rows, date_rows = _calendar_rows(calendar)
    with engine.begin() as connection:
        weeks_inserted = _insert_ignore(
            connection, CalendarWeek, week_rows, ["wm_yr_wk"]
        )
        dates_inserted = _insert_ignore(connection, M5CalendarDate, date_rows, ["d"])
        products_upserted = _upsert_products(
            connection, paths.sales, set(selected_item_ids)
        )

    with Session(engine) as session, session.begin():
        store_ids = _map_stores(
            session, pd.read_csv(paths.sales, usecols=SALES_METADATA_COLUMNS)
        )
    with engine.begin() as connection:
        catalog_cleanup = reconcile_database_to_m5_subset(
            connection,
            set(selected_item_ids),
            set(selected_store_ids),
            require_fixed_size=enforce_expected_dimensions,
        )
    with Session(engine) as session:
        product_ids = {
            item_id: product_id
            for item_id, product_id in session.execute(
                select(Product.m5_item_id, Product.id).where(
                    Product.m5_item_id.in_(selected_item_ids)
                )
            )
        }
        calendar_date_ids = {
            day_id: row_id
            for day_id, row_id in session.execute(
                select(M5CalendarDate.m5_day_id, M5CalendarDate.id)
            )
        }
        week_ids = {
            week: week_id
            for week, week_id in session.execute(
                select(CalendarWeek.wm_yr_wk, CalendarWeek.id)
            )
        }
    report["mappings"].update(
        {
            "products_mapped": len(product_ids),
            "stores_mapped": len(store_ids),
            "calendar_days_mapped": len(calendar_date_ids),
            "weeks_mapped": len(week_ids),
        }
    )
    report["ingestion"].update(
        {
            "calendar_days_processed": len(date_rows),
            "calendar_days_inserted": dates_inserted,
            "calendar_days_skipped_as_existing": len(date_rows) - dates_inserted,
            "calendar_weeks_processed": len(week_rows),
            "calendar_weeks_inserted": weeks_inserted,
            "calendar_weeks_skipped_as_existing": len(week_rows) - weeks_inserted,
            "products_available_in_source": int(
                report["mappings"]["products_in_source"]
            ),
            "products_mapped": len(selected_item_ids),
            "products_upserted": products_upserted,
            "sales_updated": 0,
            "sales_records_rejected": 0,
            "sell_prices_updated": 0,
            "sell_price_records_rejected": 0,
            "stores_removed": catalog_cleanup["stores_removed"],
            "out_of_scope_products_removed": catalog_cleanup["products_removed"],
            "obsolete_inventory_records_removed": catalog_cleanup[
                "inventory_records_removed"
            ],
            "out_of_scope_sales_removed": catalog_cleanup["sales_removed"],
            "out_of_scope_prices_removed": catalog_cleanup["prices_removed"],
        }
    )

    sales_inserted = 0
    selected_series_processed = 0
    selected_sales_units_total = 0
    sales_connection = engine.connect() if engine.dialect.name == "postgresql" else None
    if sales_connection is not None:
        sales_connection.exec_driver_sql(
            "CREATE TEMP TABLE m5_sales_stage (product_id integer, store_id integer, "
            "calendar_date_id integer, units_sold integer, source_dataset varchar(64)) "
            "ON COMMIT PRESERVE ROWS"
        )
        sales_connection.commit()
    try:
        for frame in pd.read_csv(paths.sales, chunksize=chunksize):
            frame = frame[frame["item_id"].astype(str).isin(selected_item_ids)]
            if frame.empty:
                continue
            selected_series_processed += len(frame)
            daily_columns = [
                column for column in frame.columns if column.startswith("d_")
            ]
            selected_sales_units_total += int(
                frame[daily_columns].apply(pd.to_numeric, errors="coerce").sum().sum()
            )
            long = frame.melt(
                id_vars=SALES_METADATA_COLUMNS,
                value_vars=[c for c in frame.columns if c.startswith("d_")],
                var_name="d",
                value_name="units_sold",
            )
            long["product_id"] = long["item_id"].map(product_ids)
            long["store_internal_id"] = long["store_id"].map(store_ids)
            long["calendar_date_id"] = long["d"].map(calendar_date_ids)
            if (
                long[["product_id", "store_internal_id", "calendar_date_id"]]
                .isna()
                .any()
                .any()
            ):
                raise ValueError(
                    "Sales rows contain unmapped product, store, or calendar IDs"
                )
            long["units_sold"] = long["units_sold"].astype("int64")
            cols = ["product_id", "store_internal_id", "calendar_date_id", "units_sold"]
            rows = (
                long[cols]
                .rename(columns={"store_internal_id": "store_id"})
                .to_dict(orient="records")
            )
            for row in rows:
                row["source_dataset"] = DATASET_NAME
            for offset in range(0, len(rows), INSERT_BATCH_SIZE):
                batch = rows[offset : offset + INSERT_BATCH_SIZE]
                if sales_connection is not None:
                    sales_inserted += _postgres_copy_batch(
                        sales_connection,
                        "m5_sales_stage",
                        "daily_sales_records",
                        [
                            "product_id",
                            "store_id",
                            "calendar_date_id",
                            "units_sold",
                            "source_dataset",
                        ],
                        batch,
                        ["product_id", "store_id", "calendar_date_id"],
                    )
                else:
                    with engine.begin() as connection:
                        sales_inserted += _insert_ignore(
                            connection,
                            DailySalesRecord,
                            batch,
                            ["product_id", "store_id", "calendar_date_id"],
                        )
    finally:
        if sales_connection is not None:
            sales_connection.close()
    report["ingestion"]["sales_inserted"] = sales_inserted
    report["ingestion"]["sales_series_processed"] = selected_series_processed
    report["ingestion"]["sales_processed"] = selected_series_processed * int(
        report["source_files"][SALES_FILE]["daily_columns"]
    )
    report["ingestion"]["sales_skipped_as_existing"] = (
        report["ingestion"]["sales_processed"] - sales_inserted
    )

    price_inserted = 0
    selected_price_rows = 0
    price_connection = engine.connect() if engine.dialect.name == "postgresql" else None
    if price_connection is not None:
        price_connection.exec_driver_sql(
            "CREATE TEMP TABLE m5_price_stage (product_id integer, store_id integer, "
            "calendar_week_id integer, sell_price numeric(12, 4)) ON COMMIT PRESERVE ROWS"
        )
        price_connection.commit()
    try:
        for frame in pd.read_csv(paths.prices, chunksize=100_000):
            frame = frame[
                frame["item_id"].astype(str).isin(selected_item_ids)
                & frame["store_id"].astype(str).isin(selected_store_ids)
            ]
            if frame.empty:
                continue
            selected_price_rows += len(frame)
            frame["product_id"] = frame["item_id"].map(product_ids)
            frame["calendar_week_id"] = frame["wm_yr_wk"].astype(str).map(week_ids)
            frame["store_internal_id"] = frame["store_id"].map(store_ids)
            if (
                frame[["product_id", "calendar_week_id", "store_internal_id"]]
                .isna()
                .any()
                .any()
            ):
                raise ValueError(
                    "Price rows contain unmapped product, store, or week IDs"
                )
            rows = (
                frame[
                    [
                        "product_id",
                        "store_internal_id",
                        "calendar_week_id",
                        "sell_price",
                    ]
                ]
                .rename(columns={"store_internal_id": "store_id"})
                .to_dict(orient="records")
            )
            for offset in range(0, len(rows), INSERT_BATCH_SIZE):
                batch = rows[offset : offset + INSERT_BATCH_SIZE]
                if price_connection is not None:
                    price_inserted += _postgres_copy_batch(
                        price_connection,
                        "m5_price_stage",
                        "weekly_sell_prices",
                        ["product_id", "store_id", "calendar_week_id", "sell_price"],
                        batch,
                        ["product_id", "store_id", "calendar_week_id"],
                    )
                else:
                    with engine.begin() as connection:
                        price_inserted += _insert_ignore(
                            connection,
                            WeeklySellPrice,
                            batch,
                            ["product_id", "store_id", "calendar_week_id"],
                        )
    finally:
        if price_connection is not None:
            price_connection.close()
    report["ingestion"]["sell_prices_inserted"] = price_inserted
    report["ingestion"]["sell_prices_processed"] = selected_price_rows
    report["ingestion"]["sell_prices_skipped_as_existing"] = (
        report["ingestion"]["sell_prices_processed"] - price_inserted
    )
    report["status"] = "ingested"
    report["sales_reconciliation"] = {
        "expected_sales_records": report["ingestion"]["sales_processed"],
        "inserted_sales_records": sales_inserted,
        "reconciled": sales_inserted + report["ingestion"]["sales_skipped_as_existing"]
        == report["ingestion"]["sales_processed"],
        "source_sales_units_total": selected_sales_units_total,
    }
    with Session(engine) as session:
        database_sales_total = session.scalar(
            select(func.coalesce(func.sum(DailySalesRecord.units_sold), 0)).where(
                DailySalesRecord.source_dataset == DATASET_NAME
            )
        )
    report["sales_reconciliation"]["database_sales_units_total"] = int(
        database_sales_total or 0
    )
    report["sales_reconciliation"]["units_reconciled"] = (
        int(database_sales_total or 0) == selected_sales_units_total
    )
    report["data_provenance"] = {
        "historical_sales_calendar_prices_and_identifiers": "original M5 Forecasting source records",
        "products_not_selected": "not imported; only the 50 selected M5 item IDs are in the product table",
        "unit_cost": "unknown in M5; required model field is zero placeholder, not a source value",
        "store_coordinates": "approximate state centroids; not verified store addresses",
        "manufacturer_distributors_warehouses_trucks_drivers": "assumed project infrastructure, not supplied by M5",
        "inventory_history_and_lead_times": "separate reproducible synthetic simulations, not historical Walmart operational data",
    }
    with Session(engine) as session:
        actual_product_count = session.scalar(select(func.count()).select_from(Product))
        actual_store_count = session.scalar(select(func.count()).select_from(Store))
        actual_sales_count = session.scalar(
            select(func.count())
            .select_from(DailySalesRecord)
            .where(DailySalesRecord.source_dataset == DATASET_NAME)
        )
        actual_price_count = session.scalar(
            select(func.count()).select_from(WeeklySellPrice)
        )
        actual_product_ids = set(
            session.scalars(
                select(Product.m5_item_id).where(Product.m5_item_id.is_not(None))
            )
        )
        actual_store_ids = set(
            session.scalars(
                select(Store.m5_store_id).where(Store.m5_store_id.is_not(None))
            )
        )
        sales_product_ids = set(
            session.scalars(
                select(Product.m5_item_id)
                .join(DailySalesRecord, DailySalesRecord.product_id == Product.id)
                .where(DailySalesRecord.source_dataset == DATASET_NAME)
                .distinct()
            )
        )
        sales_store_ids = set(
            session.scalars(
                select(Store.m5_store_id)
                .join(DailySalesRecord, DailySalesRecord.store_id == Store.id)
                .where(DailySalesRecord.source_dataset == DATASET_NAME)
                .distinct()
            )
        )
        price_product_ids = set(
            session.scalars(
                select(Product.m5_item_id)
                .join(WeeklySellPrice, WeeklySellPrice.product_id == Product.id)
                .distinct()
            )
        )
        price_store_ids = set(
            session.scalars(
                select(Store.m5_store_id)
                .join(WeeklySellPrice, WeeklySellPrice.store_id == Store.id)
                .distinct()
            )
        )
        actual_calendar_day_count = session.scalar(
            select(func.count()).select_from(M5CalendarDate)
        )
        actual_calendar_week_count = session.scalar(
            select(func.count()).select_from(CalendarWeek)
        )
        distributor_ids = list(
            session.scalars(select(Distributor.id).order_by(Distributor.id))
        )
        store_assignments = {
            store_id: distributor_id
            for store_id, distributor_id in session.execute(
                select(Store.m5_store_id, Store.distributor_id).where(
                    Store.m5_store_id.is_not(None)
                )
            )
        }
    report["database_validation"] = {
        "selected_product_count_and_no_synthetic_products": actual_product_count
        == len(selected_item_ids),
        "exactly_10_stores_and_no_synthetic_stores": actual_store_count == 10,
        "product_ids_match_selected_sample": actual_product_ids
        == set(selected_item_ids),
        "store_ids_match_official_m5_set": actual_store_ids == set(M5_STORE_IDS),
        "sales_rows_match_selected_source": actual_sales_count
        == report["ingestion"]["sales_processed"],
        "weekly_price_rows_match_selected_source": actual_price_count
        == report["ingestion"]["sell_prices_processed"],
        "sales_reference_only_selected_m5_ids": sales_product_ids
        == set(selected_item_ids)
        and sales_store_ids == set(M5_STORE_IDS),
        "prices_reference_only_selected_m5_ids": price_product_ids
        == set(selected_item_ids)
        and price_store_ids == set(M5_STORE_IDS),
        "calendar_dates_and_weeks_match_source": actual_calendar_day_count
        == len(date_rows)
        and actual_calendar_week_count == len(week_rows),
        "five_stores_assigned_to_each_distributor": len(distributor_ids) >= 2
        and sum(
            store_assignments.get(store_id) == distributor_ids[0]
            for store_id in M5_STORE_IDS
        )
        == 5
        and sum(
            store_assignments.get(store_id) == distributor_ids[1]
            for store_id in M5_STORE_IDS
        )
        == 5,
        "sales_units_reconcile": report["sales_reconciliation"]["units_reconciled"],
    }
    report["raw_files_unchanged_during_ingestion"] = report[
        "raw_file_fingerprints_before_ingestion"
    ] == _raw_file_fingerprints(paths)
    report["database_validation"]["raw_files_unchanged"] = report[
        "raw_files_unchanged_during_ingestion"
    ]
    report["status"] = (
        "ingested"
        if all(report["database_validation"].values())
        and report["sales_reconciliation"]["reconciled"]
        else "validation_failed"
    )
    report["checks"] = {
        name: {"status": "passed" if passed else "failed"}
        for name, passed in report["database_validation"].items()
    }
    report["checks"]["source_validation"] = {"status": "passed"}
    report["checks"]["no_rejected_source_records"] = {
        "status": (
            "passed"
            if not any(report.get("rejected_records", {}).values())
            else "failed"
        )
    }
    report["pipeline_execution_seconds"] = round(
        time.perf_counter() - pipeline_started, 3
    )
    write_quality_report(report, report_path)
    return report


def simulate_inventory_history(
    daily_sales: pd.DataFrame, opening_days: float = 5.0, reorder_days: float = 2.0
) -> pd.DataFrame:
    """Replay a synthetic stock policy using observed sales only as a demand proxy."""
    required = {"item_id", "store_id", "date", "units_sold"}
    if not required.issubset(daily_sales.columns):
        raise ValueError(f"daily_sales requires columns {sorted(required)}")
    output: list[dict[str, Any]] = []
    ordered = daily_sales.sort_values(["item_id", "store_id", "date"])
    for (item_id, store_id), group in ordered.groupby(
        ["item_id", "store_id"], sort=False
    ):
        sales = group["units_sold"].astype(int).tolist()
        avg = float(np.mean(sales)) if sales else 0.0
        target = max(1, math.ceil(avg * opening_days))
        reorder = max(0, math.ceil(avg * reorder_days))
        stock = target
        for row, demand in zip(group.to_dict(orient="records"), sales, strict=True):
            opening = stock
            fulfilled = min(opening, demand)
            confirmed_shortage = demand > opening
            potential_stockout = confirmed_shortage or (
                demand > 0 and opening <= reorder
            )
            after_sales = opening - fulfilled
            replenishment = target - after_sales if after_sales <= reorder else 0
            stock = after_sales + replenishment
            if confirmed_shortage:
                classification = "simulated_confirmed_stockout"
            elif potential_stockout:
                classification = "potential_stockout_risk"
            elif demand == 0:
                classification = "observed_zero_sales_no_stockout_evidence"
            else:
                classification = "no_stockout_in_simulation"
            output.append(
                {
                    "item_id": item_id,
                    "store_id": store_id,
                    "date": row["date"],
                    "opening_inventory": opening,
                    "demand_units": demand,
                    "observed_sales_units": demand,
                    "fulfilled_units": fulfilled,
                    "potential_stockout": potential_stockout,
                    "simulated_confirmed_stockout": confirmed_shortage,
                    "stockout_classification": classification,
                    "simulated_unmet_demand_units": demand - fulfilled,
                    "replenishment_units": replenishment,
                    "replenishment_event": replenishment > 0,
                    "closing_inventory": stock,
                    "excess_inventory_units": max(stock - target, 0),
                    "demand_proxy_assumption": (
                        "observed M5 sales used as a simulated demand proxy; "
                        "not actual unconstrained demand"
                    ),
                    "history_type": "synthetic_simulation_not_actual_walmart_inventory",
                }
            )
    return pd.DataFrame(output)


def generate_lead_times(
    lanes: list[dict[str, str]],
    samples_per_lane: int = 100,
    seed: int = 2026,
    lane_parameters: dict[str, dict[str, float]] | None = None,
) -> pd.DataFrame:
    """Generate reproducible, positive synthetic lane lead times with a lognormal tail."""
    if samples_per_lane <= 0:
        raise ValueError("samples_per_lane must be positive")
    rng = np.random.default_rng(seed)
    rows: list[dict[str, Any]] = []
    for lane in lanes:
        lane_type = lane["lane_type"]
        defaults = {
            "manufacturer_to_distributor": {"median_days": 4.0, "sigma": 0.65},
            "warehouse_to_store": {"median_days": 1.25, "sigma": 0.65},
        }
        if lane_type not in defaults:
            raise ValueError(f"Unsupported lead-time lane type: {lane_type}")
        parameters = (lane_parameters or {}).get(lane_type, defaults[lane_type])
        median = float(parameters["median_days"])
        sigma = float(parameters["sigma"])
        if median <= 0 or sigma < 0:
            raise ValueError("Lead-time median must be positive and sigma nonnegative")
        values = rng.lognormal(
            mean=math.log(median), sigma=sigma, size=samples_per_lane
        )
        for sample_index, value in enumerate(values, start=1):
            rows.append(
                {
                    **lane,
                    "sample_id": sample_index,
                    "lead_time_days": round(max(float(value), 0.1), 2),
                    "median_parameter_days": median,
                    "sigma_parameter": sigma,
                    "generation_type": "synthetic_lognormal_heavy_tail",
                    "seed": seed,
                }
            )
    return pd.DataFrame(rows)


def generate_synthetic_artifacts(
    engine: Engine, output_dir: Path, seed: int = 2026
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    inventory_path = output_dir / "synthetic_inventory_history.csv.gz"
    inventory_fields = [
        "item_id",
        "store_id",
        "date",
        "opening_inventory",
        "demand_units",
        "observed_sales_units",
        "fulfilled_units",
        "potential_stockout",
        "simulated_confirmed_stockout",
        "stockout_classification",
        "simulated_unmet_demand_units",
        "replenishment_units",
        "replenishment_event",
        "closing_inventory",
        "excess_inventory_units",
        "demand_proxy_assumption",
        "history_type",
    ]
    rows_written = 0
    stockout_rows = 0
    confirmed_stockout_rows = 0
    unmet_demand_units = 0
    excess_inventory_rows = 0
    replenishment_events = 0
    query = (
        select(
            Product.m5_item_id,
            Store.m5_store_id,
            M5CalendarDate.date,
            DailySalesRecord.units_sold,
        )
        .join(Product, Product.id == DailySalesRecord.product_id)
        .join(Store, Store.id == DailySalesRecord.store_id)
        .join(M5CalendarDate, M5CalendarDate.id == DailySalesRecord.calendar_date_id)
        .where(DailySalesRecord.source_dataset == DATASET_NAME)
        .order_by(Product.m5_item_id, Store.m5_store_id, M5CalendarDate.date)
    )
    with (
        engine.connect().execution_options(stream_results=True) as connection,
        gzip.open(inventory_path, "wt", newline="", encoding="utf-8") as stream,
    ):
        import csv

        writer = csv.DictWriter(stream, fieldnames=inventory_fields)
        writer.writeheader()
        result = connection.execute(query)
        current_key: tuple[str | None, str | None] | None = None
        records: list[dict[str, Any]] = []
        for item_id, store_id, day, units in result:
            key = (item_id, store_id)
            if current_key is not None and current_key != key:
                simulated = simulate_inventory_history(pd.DataFrame(records))
                writer.writerows(simulated.to_dict(orient="records"))
                rows_written += len(simulated)
                stockout_rows += int(simulated["potential_stockout"].sum())
                confirmed_stockout_rows += int(
                    simulated["simulated_confirmed_stockout"].sum()
                )
                unmet_demand_units += int(
                    simulated["simulated_unmet_demand_units"].sum()
                )
                excess_inventory_rows += int(
                    (simulated["excess_inventory_units"] > 0).sum()
                )
                replenishment_events += int(simulated["replenishment_event"].sum())
                records = []
            current_key = key
            records.append(
                {
                    "item_id": item_id,
                    "store_id": store_id,
                    "date": day,
                    "units_sold": units,
                }
            )
        if records:
            simulated = simulate_inventory_history(pd.DataFrame(records))
            writer.writerows(simulated.to_dict(orient="records"))
            rows_written += len(simulated)
            stockout_rows += int(simulated["potential_stockout"].sum())
            confirmed_stockout_rows += int(
                simulated["simulated_confirmed_stockout"].sum()
            )
            unmet_demand_units += int(simulated["simulated_unmet_demand_units"].sum())
            excess_inventory_rows += int(
                (simulated["excess_inventory_units"] > 0).sum()
            )
            replenishment_events += int(simulated["replenishment_event"].sum())

    with Session(engine) as session:
        distributors = list(
            session.scalars(select(Distributor).order_by(Distributor.id))
        )
        warehouses = list(session.scalars(select(Warehouse).order_by(Warehouse.id)))
        stores = list(session.scalars(select(Store).order_by(Store.id)))
        manufacturers = list(
            session.scalars(select(Manufacturer).order_by(Manufacturer.id))
        )
        lanes: list[dict[str, str]] = []
        if manufacturers:
            for distributor in distributors:
                lanes.append(
                    {
                        "lane_type": "manufacturer_to_distributor",
                        "origin": manufacturers[0].name,
                        "destination": distributor.name,
                    }
                )
        warehouse_by_id = {warehouse.id: warehouse for warehouse in warehouses}
        for store in stores:
            warehouse = warehouse_by_id[store.assigned_warehouse_id]
            lanes.append(
                {
                    "lane_type": "warehouse_to_store",
                    "origin": warehouse.name,
                    "destination": store.name,
                }
            )
    lead_times = generate_lead_times(lanes, seed=seed)
    lead_path = output_dir / "synthetic_lane_lead_times.csv"
    lead_times.to_csv(lead_path, index=False)
    stats = {
        "inventory_history": str(inventory_path),
        "inventory_rows": rows_written,
        "potential_stockout_rows": stockout_rows,
        "simulated_confirmed_stockout_rows": confirmed_stockout_rows,
        "simulated_unmet_demand_units": unmet_demand_units,
        "excess_inventory_rows": excess_inventory_rows,
        "replenishment_events": replenishment_events,
        "lead_time_file": str(lead_path),
        "lead_time_rows": len(lead_times),
        "lead_time_min_days": (
            float(lead_times["lead_time_days"].min()) if len(lead_times) else None
        ),
        "lead_time_median_days": (
            float(lead_times["lead_time_days"].median()) if len(lead_times) else None
        ),
        "lead_time_p95_days": (
            float(lead_times["lead_time_days"].quantile(0.95))
            if len(lead_times)
            else None
        ),
        "lead_time_max_days": (
            float(lead_times["lead_time_days"].max()) if len(lead_times) else None
        ),
        "seed": seed,
        "lead_time_parameters": {
            "manufacturer_to_distributor": {"median_days": 4.0, "sigma": 0.65},
            "warehouse_to_store": {"median_days": 1.25, "sigma": 0.65},
        },
        "assumptions": {
            "inventory": "Opening stock is five days of mean observed sales; when closing stock reaches two mean-sales days, immediate assumed replenishment restores the target. Observed sales are only a demand proxy. A simulation shortage is confirmed only inside this modeled scenario, never as a historical Walmart stockout. Zero sales is explicitly not a stockout.",
            "coordinates": "M5 has no store coordinates. Store coordinates are approximate state centroids and are not actual store addresses or verified Walmart locations.",
            "infrastructure": "Manufacturer, distributors, warehouses, trucks, drivers, warehouse assignments, replenishment, and transportation are assumed project entities, not M5 source data.",
            "lead_times": "100 reproducible lognormal samples per manufacturer-distributor and assigned warehouse-store lane; each row stores its median and sigma assumptions.",
            "provenance": "Synthetic scenarios only; these values are not historical Walmart inventory or transportation records.",
        },
    }
    return stats


def write_quality_report(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")
    markdown_path = path.with_suffix(".md")
    source_lines = [
        "| File | Rows | Columns |",
        "| --- | ---: | ---: |",
    ]
    for filename, details in report.get("source_files", {}).items():
        source_lines.append(
            f"| `{filename}` | {details.get('rows', 'n/a')} | {details.get('columns', 'n/a')} |"
        )
    check_lines = [
        f"- `{name}`: **{(details.get('status', 'unknown') if isinstance(details, dict) else ('passed' if details else 'failed')).upper()}**"
        for name, details in report.get("checks", {}).items()
    ] or ["- No database ingestion checks were run."]
    mappings = report.get("mappings", {})
    ingestion = report.get("ingestion", {})
    reconciliation = report.get("sales_reconciliation", {})
    synthetic = report.get("synthetic_inventory", {})
    markdown_path.write_text(
        "# M5 data ingestion quality report\n\n"
        f"- Overall status: **{str(report.get('status', 'unknown')).upper()}**\n"
        f"- Pipeline execution: `{report.get('pipeline_execution_seconds', 'not recorded')}` seconds\n"
        f"- Validation errors: `{len(report.get('validation_errors', []))}`\n\n"
        "## Source files\n\n" + "\n".join(source_lines) + "\n\n## Source quality\n\n"
        f"- Missing values by file: `{json.dumps(report.get('missing_values', {}), default=str)}`\n"
        f"- Duplicate records by file: `{json.dumps(report.get('duplicate_records', {}), default=str)}`\n"
        f"- Invalid values by file: `{json.dumps(report.get('invalid_records', {}), default=str)}`\n"
        f"- Rejected source records/values: `{json.dumps(report.get('rejected_records', {}), default=str)}`\n"
        f"- Validation errors: `{json.dumps(report.get('validation_errors', []))}`\n\n"
        "## M5 selection and ingestion\n\n"
        f"- Selected products: `{mappings.get('selected_products', 0)}`\n"
        f"- Selected item IDs: `{json.dumps(mappings.get('selected_item_ids', []))}`\n"
        f"- Mapped M5 stores: `{json.dumps(mappings.get('selected_store_ids', []))}`\n"
        f"- Product-store series: `{mappings.get('selected_product_store_series', 0)}`\n"
        f"- Ingestion counts: `{json.dumps(ingestion, default=str)}`\n"
        f"- Sales reconciliation: `{json.dumps(reconciliation, default=str)}`\n\n"
        "## Synthetic derived artifacts\n\n"
        f"- Inventory replay and lead-time summary: `{json.dumps(synthetic, default=str)}`\n\n"
        "## Acceptance checks\n\n" + "\n".join(check_lines) + "\n\n## Provenance\n\n"
        "Daily sales, calendar dates/events, product/store identifiers, and weekly prices in the ingestion tables come from the original M5 files. "
        "Manufacturer/distributor/warehouse/truck/driver entities and warehouse assignments are assumed project infrastructure. Store coordinates are approximate state centroids, not verified store addresses. "
        "Inventory histories and lane lead times are separate synthetic simulations; they are not historical Walmart operational records.\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate and ingest M5 CSVs; no source data is fabricated"
    )
    parser.add_argument("--raw-dir", type=Path, default=Path("../data/raw/m5"))
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("../docs/data/m5_ingestion_quality_report.json"),
    )
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    parser.add_argument(
        "--synthetic-only",
        action="store_true",
        help="Generate synthetic lane lead times; inventory requires ingested M5 sales",
    )
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    pipeline_started = time.perf_counter()
    raw_dir = args.raw_dir.resolve()
    report_path = args.report.resolve()
    paths = M5Paths.from_raw_dir(raw_dir)
    if paths.missing() and raw_dir.name.lower() == "m5":
        parent_paths = M5Paths.from_raw_dir(raw_dir.parent)
        if len(parent_paths.missing()) < len(paths.missing()):
            paths = parent_paths
    if args.synthetic_only:
        if not args.database_url:
            parser.error(
                "DATABASE_URL is required for synthetic-only artifact generation"
            )
        from sqlalchemy import create_engine

        stats = generate_synthetic_artifacts(
            create_engine(args.database_url),
            Path("../data/processed").resolve(),
            args.seed,
        )
        source_audit = inspect_and_validate(paths)
        report = {
            "dataset": DATASET_NAME,
            "status": "synthetic_artifacts_generated",
            "m5_source_status": source_audit["status"],
            "missing_files": source_audit.get("missing_files", []),
            "source_files": source_audit.get("source_files", {}),
            "missing_values": source_audit.get("missing_values", {}),
            "duplicate_records": source_audit.get("duplicate_records", {}),
            "invalid_records": source_audit.get("invalid_records", {}),
            "validation_errors": source_audit.get("validation_errors", []),
            "synthetic_inventory": stats,
            "checks": {
                "synthetic_artifacts_generated": {"status": "passed"},
                "m5_source_files_available": {
                    "status": (
                        "passed" if not source_audit.get("missing_files") else "failed"
                    )
                },
            },
            "pipeline_execution_seconds": round(
                time.perf_counter() - pipeline_started, 3
            ),
        }
        write_quality_report(report, report_path)
        print(json.dumps(report, indent=2))
        return
    if paths.missing():
        report = inspect_and_validate(paths)
        report["pipeline_execution_seconds"] = round(
            time.perf_counter() - pipeline_started, 3
        )
        write_quality_report(report, report_path)
        print(report["download_instructions"])
        print(f"Ingestion stopped gracefully; report written to {report_path}")
        return
    if not args.database_url:
        parser.error("DATABASE_URL is required when all M5 files are present")
    from sqlalchemy import create_engine

    report = ingest_m5(
        create_engine(args.database_url),
        paths,
        report_path,
        product_limit=50,
    )
    print(json.dumps(report, indent=2, default=str))
    if report["status"] == "ingested" and report.get("sales_reconciliation", {}).get(
        "reconciled"
    ):
        synthetic = generate_synthetic_artifacts(
            create_engine(args.database_url),
            Path("../data/processed").resolve(),
            args.seed,
        )
        report["synthetic_inventory"] = synthetic
        report["pipeline_execution_seconds"] = round(
            time.perf_counter() - pipeline_started, 3
        )
        report["checks"]["synthetic_inventory_generated"] = {
            "status": "passed" if synthetic["inventory_rows"] > 0 else "failed"
        }
        report["checks"]["synthetic_lead_times_generated"] = {
            "status": "passed" if synthetic["lead_time_rows"] > 0 else "failed"
        }
        write_quality_report(report, report_path)
        if any(check["status"] != "passed" for check in report["checks"].values()):
            raise SystemExit("One or more ingestion acceptance checks failed")
    else:
        raise SystemExit(
            f"M5 ingestion did not pass acceptance checks (status={report['status']}); see {report_path}"
        )


if __name__ == "__main__":
    main()
