# M5 data ingestion quality report

- Status: `ingested`
- M5 source status: `ingested`
- Source files: `{"calendar.csv": {"rows": 2, "columns": 14, "column_names": ["d", "date", "wm_yr_wk", "weekday", "wday", "month", "year", "event_name_1", "event_type_1", "event_name_2", "event_type_2", "snap_CA", "snap_TX", "snap_WI"]}, "sales_train_validation.csv": {"rows": 1, "columns": 8, "column_names": ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id", "d_1", "d_2"], "product_store_series": 1, "daily_columns": 2}, "sell_prices.csv": {"rows": 1, "columns": 4, "column_names": ["store_id", "item_id", "wm_yr_wk", "sell_price"]}}`
- Missing values: `{"calendar.csv": 0, "sales_train_validation.csv": 0, "sell_prices.csv": 0}`
- Duplicate records: `{"calendar.csv": 0, "sales_train_validation.csv": 0, "sell_prices.csv": 0}`
- Invalid records: `{"sales_values": 0, "selling_prices": 0}`
- Mappings: `{"products_in_source": 1, "stores_in_source": 1, "sales_day_columns_not_in_calendar": [], "price_rows_with_unmapped_references": 0, "products_mapped": 1, "stores_mapped": 1, "calendar_days_mapped": 2, "weeks_mapped": 1}`
- Ingestion: `{"records_inserted": 0, "records_skipped_as_existing": 0, "calendar_days_processed": 2, "calendar_days_inserted": 0, "calendar_days_skipped_as_existing": 2, "calendar_weeks_processed": 1, "calendar_weeks_inserted": 0, "calendar_weeks_skipped_as_existing": 1, "products_in_catalogue": 1, "products_upserted": 1, "sales_inserted": 0, "sales_processed": 2, "sales_skipped_as_existing": 2, "sell_prices_inserted": 0, "sell_prices_processed": 1, "sell_prices_skipped_as_existing": 1}`
- Synthetic inventory / lead times: `{}`
- Validation errors: `[]`

Synthetic inventory and lead-time outputs, when generated, are separate artifacts and do not represent actual Walmart operations.
