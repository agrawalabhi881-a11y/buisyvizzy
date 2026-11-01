# Phase 3: original M5 subset ingestion

The development database uses exactly the 10 official M5 stores and a stable, department-balanced selection of 50 genuine `item_id` values. Product selection ranks items by the number of valid store-week price records, then uses the item ID as a deterministic tie-breaker. The loader reads the wider source to validate and select records but inserts only the selected 50 products; the other 2,999 products are not imported.

## Source files

Put the unmodified Kaggle files under `data/raw/m5/` (the extracted competition folder may remain nested):

- Required: `sales_train_validation.csv`, `calendar.csv`, `sell_prices.csv`.
- Validated when present: `sales_train_evaluation.csv`, `sample_submission.csv`.

```powershell
kaggle competitions download -c m5-forecasting-accuracy -p data/raw/m5
Expand-Archive data/raw/m5/m5-forecasting-accuracy.zip -DestinationPath data/raw/m5
```

Raw files are read-only inputs and excluded from Git. The quality report records dimensions, nulls, duplicates, invalid values, reference mappings and SHA-256 fingerprints.

## Database seed and ingestion

With an already migrated PostgreSQL database and `DATABASE_URL`, run from `backend/`:

```powershell
python -m scripts.seed
python -m app.ingestion.m5
```

The seed obtains its catalog directly from the M5 files. It keeps original external IDs and displays stores as `Store 1` through `Store 10`. Exactly five stores are assigned to each distributor, with each store assigned to a warehouse owned by that distributor. Re-running the seed or loader is idempotent.

Before pruning prior catalog entries, the code checks product/store foreign-key dependents and stock balances. It refuses to delete records with nonzero or reserved stock, orders, shipments, unmet-demand records, or disruptions that depend on obsolete stores/products. Empty zero-stock synthetic product/store seed records and their inventory placeholders are removed; manufacturer, distributors, warehouses, trucks and drivers are preserved. No M5 inventory quantities are invented or inserted into the live inventory table.

Sales are loaded for all selected product-store pairs and all 1,913 training days (up to 956,500 rows) in bounded chunks with conflict-safe batches. Weekly prices are filtered to the selected items and official stores. Calendar dates, events, SNAP values and weeks use the original M5 fields. Ingestion is rerunnable; records already present are reported as skipped.

## Provenance and limitations

Daily sales, calendar, item IDs, store IDs, departments/categories and weekly prices are original M5 data. M5 does not provide product costs, warehouse, distributor, truck, driver, inventory or transportation records. The product model's required `unit_cost` is set to zero as an unknown placeholder, not a Walmart cost. Infrastructure entities and assignments are assumptions. Since M5 has no store addresses or coordinates, each store is assigned a coarse state-centroid approximation, labelled `approximate_state_centroid_not_store_address`; these coordinates must not be treated as verified Walmart locations.

The separate `data/processed/synthetic_inventory_history.csv.gz` is a policy replay, not actual inventory history. It uses observed M5 sales only as a demand proxy, records replenishment and excess inventory, and distinguishes zero sales, potential stockout risk, and a shortage confirmed within the simulation. Simulated unmet demand is not observed Walmart lost sales. Lane lead times are reproducible lognormal samples for assumed manufacturer-distributor and warehouse-store lanes; their parameters and seed are recorded. Neither generated artifact modifies raw M5 files or the live inventory table.

## Quality report

After ingestion, inspect [`m5_ingestion_quality_report.md`](m5_ingestion_quality_report.md) and its JSON companion. They include exact selected identifiers, source and database counts, inserted/skipped/rejected records, reconciliation, pass/fail checks, synthetic replay metrics, lead-time statistics, source fingerprints and pipeline execution time.
