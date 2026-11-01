# M5 data ingestion quality report

- Overall status: **INGESTED**
- Pipeline execution: `485.246` seconds
- Validation errors: `0`

## Source files

| File | Rows | Columns |
| --- | ---: | ---: |
| `calendar.csv` | 1969 | 14 |
| `sales_train_validation.csv` | 30490 | 1919 |
| `sell_prices.csv` | 6841121 | 4 |
| `sales_train_evaluation.csv` | 30490 | 1947 |
| `sample_submission.csv` | 60980 | 29 |

## Source quality

- Missing values by file: `{"calendar.csv": {"event_name_1": 1807, "event_type_1": 1807, "event_name_2": 1964, "event_type_2": 1964}, "sales_train_validation.csv": {}, "sell_prices.csv": {}, "sales_train_evaluation.csv": {}, "sample_submission.csv": {}}`
- Duplicate records by file: `{"calendar.csv": 0, "sales_train_validation.csv": 0, "sell_prices.csv": 0, "sales_train_evaluation.csv": 0, "sample_submission.csv": 0}`
- Invalid values by file: `{"sales_values": 0, "selling_prices": 0, "sales_train_evaluation.csv": 0, "sample_submission.csv": {"forecast_values": 0, "unmapped_series_identifiers": 0}}`
- Rejected source records/values: `{"calendar_rows": 0, "sales_rows_or_values": 0, "price_rows": 0}`
- Validation errors: `[]`

## M5 selection and ingestion

- Selected products: `50`
- Selected item IDs: `["FOODS_1_003", "FOODS_2_013", "FOODS_3_014", "HOBBIES_1_010", "HOBBIES_2_009", "HOUSEHOLD_1_011", "HOUSEHOLD_2_030", "FOODS_1_006", "FOODS_2_026", "FOODS_3_020", "HOBBIES_1_022", "HOBBIES_2_036", "HOUSEHOLD_1_016", "HOUSEHOLD_2_033", "FOODS_1_018", "FOODS_2_042", "FOODS_3_080", "HOBBIES_1_023", "HOBBIES_2_120", "HOUSEHOLD_1_025", "HOUSEHOLD_2_052", "FOODS_1_019", "FOODS_2_052", "FOODS_3_090", "HOBBIES_1_028", "HOBBIES_2_002", "HOUSEHOLD_1_034", "HOUSEHOLD_2_059", "FOODS_1_020", "FOODS_2_056", "FOODS_3_109", "HOBBIES_1_032", "HOBBIES_2_046", "HOUSEHOLD_1_038", "HOUSEHOLD_2_084", "FOODS_1_024", "FOODS_2_166", "FOODS_3_115", "HOBBIES_1_038", "HOBBIES_2_115", "HOUSEHOLD_1_046", "HOUSEHOLD_2_140", "FOODS_1_032", "FOODS_2_181", "FOODS_3_117", "HOBBIES_1_067", "HOBBIES_2_130", "HOUSEHOLD_1_048", "HOUSEHOLD_2_142", "FOODS_1_041"]`
- Mapped M5 stores: `["CA_1", "CA_2", "CA_3", "CA_4", "TX_1", "TX_2", "TX_3", "WI_1", "WI_2", "WI_3"]`
- Product-store series: `500`
- Ingestion counts: `{"records_inserted": 0, "records_skipped_as_existing": 0, "calendar_days_processed": 1969, "calendar_days_inserted": 0, "calendar_days_skipped_as_existing": 1969, "calendar_weeks_processed": 282, "calendar_weeks_inserted": 0, "calendar_weeks_skipped_as_existing": 282, "products_available_in_source": 3049, "products_mapped": 50, "products_upserted": 0, "sales_updated": 0, "sales_records_rejected": 0, "sell_prices_updated": 0, "sell_price_records_rejected": 0, "stores_removed": 0, "out_of_scope_products_removed": 3049, "obsolete_inventory_records_removed": 650, "out_of_scope_sales_removed": 899110, "out_of_scope_prices_removed": 107888, "sales_inserted": 899110, "sales_series_processed": 500, "sales_processed": 956500, "sales_skipped_as_existing": 57390, "sell_prices_inserted": 132529, "sell_prices_processed": 140987, "sell_prices_skipped_as_existing": 8458}`
- Sales reconciliation: `{"expected_sales_records": 956500, "inserted_sales_records": 899110, "reconciled": true, "source_sales_units_total": 2862425, "database_sales_units_total": 2862425, "units_reconciled": true}`

## Synthetic derived artifacts

- Inventory replay and lead-time summary: `{"inventory_history": "C:\\Users\\This_PC\\OneDrive\\Desktop\\hackathon\\bissyvissy\\data\\processed\\synthetic_inventory_history.csv.gz", "inventory_rows": 956500, "potential_stockout_rows": 23496, "simulated_confirmed_stockout_rows": 18436, "simulated_unmet_demand_units": 82693, "excess_inventory_rows": 0, "replenishment_events": 230864, "lead_time_file": "C:\\Users\\This_PC\\OneDrive\\Desktop\\hackathon\\bissyvissy\\data\\processed\\synthetic_lane_lead_times.csv", "lead_time_rows": 1200, "lead_time_min_days": 0.17, "lead_time_median_days": 1.45, "lead_time_p95_days": 6.48, "lead_time_max_days": 31.01, "seed": 2026, "lead_time_parameters": {"manufacturer_to_distributor": {"median_days": 4.0, "sigma": 0.65}, "warehouse_to_store": {"median_days": 1.25, "sigma": 0.65}}, "assumptions": {"inventory": "Opening stock is five days of mean observed sales; when closing stock reaches two mean-sales days, immediate assumed replenishment restores the target. Observed sales are only a demand proxy. A simulation shortage is confirmed only inside this modeled scenario, never as a historical Walmart stockout. Zero sales is explicitly not a stockout.", "coordinates": "M5 has no store coordinates. Store coordinates are approximate state centroids and are not actual store addresses or verified Walmart locations.", "infrastructure": "Manufacturer, distributors, warehouses, trucks, drivers, warehouse assignments, replenishment, and transportation are assumed project entities, not M5 source data.", "lead_times": "100 reproducible lognormal samples per manufacturer-distributor and assigned warehouse-store lane; each row stores its median and sigma assumptions.", "provenance": "Synthetic scenarios only; these values are not historical Walmart inventory or transportation records."}}`

## Acceptance checks

- `selected_product_count_and_no_synthetic_products`: **PASSED**
- `exactly_10_stores_and_no_synthetic_stores`: **PASSED**
- `product_ids_match_selected_sample`: **PASSED**
- `store_ids_match_official_m5_set`: **PASSED**
- `sales_rows_match_selected_source`: **PASSED**
- `weekly_price_rows_match_selected_source`: **PASSED**
- `sales_reference_only_selected_m5_ids`: **PASSED**
- `prices_reference_only_selected_m5_ids`: **PASSED**
- `calendar_dates_and_weeks_match_source`: **PASSED**
- `five_stores_assigned_to_each_distributor`: **PASSED**
- `sales_units_reconcile`: **PASSED**
- `raw_files_unchanged`: **PASSED**
- `source_validation`: **PASSED**
- `no_rejected_source_records`: **PASSED**
- `synthetic_inventory_generated`: **PASSED**
- `synthetic_lead_times_generated`: **PASSED**

## Provenance

Daily sales, calendar dates/events, product/store identifiers, and weekly prices in the ingestion tables come from the original M5 files. Manufacturer/distributor/warehouse/truck/driver entities and warehouse assignments are assumed project infrastructure. Store coordinates are approximate state centroids, not verified store addresses. Inventory histories and lane lead times are separate synthetic simulations; they are not historical Walmart operational records.
