# M5 data ingestion quality report

- Status: `invalid`
- M5 source status: `invalid`
- Source files: `{"calendar.csv": {"rows": 2, "columns": 14, "column_names": ["d", "date", "wm_yr_wk", "weekday", "wday", "month", "year", "event_name_1", "event_type_1", "event_name_2", "event_type_2", "snap_CA", "snap_TX", "snap_WI"]}, "sales_train_validation.csv": {"rows": 1, "columns": 8, "column_names": ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id", "d_1", "d_2"], "product_store_series": 1, "daily_columns": 2}, "sell_prices.csv": {"rows": 1, "columns": 4, "column_names": ["store_id", "item_id", "wm_yr_wk", "sell_price"]}}`
- Missing values: `{"calendar.csv": 0, "sales_train_validation.csv": 0, "sell_prices.csv": 0}`
- Duplicate records: `{"calendar.csv": 0, "sales_train_validation.csv": 0, "sell_prices.csv": 0}`
- Invalid records: `{"sales_values": 1, "selling_prices": 0}`
- Mappings: `{"products_in_source": 1, "stores_in_source": 1, "sales_day_columns_not_in_calendar": [], "price_rows_with_unmapped_references": 0}`
- Ingestion: `{"records_inserted": 0, "records_skipped_as_existing": 0}`
- Synthetic inventory / lead times: `{}`
- Validation errors: `["sales file contains missing/duplicate/invalid values or unmapped days"]`

Synthetic inventory and lead-time outputs, when generated, are separate artifacts and do not represent actual Walmart operations.
