# Data Dictionary

All identifiers are integer surrogate primary keys. Timestamps use timezone-aware PostgreSQL timestamps. Quantities use fixed precision decimals except daily M5 unit sales (integer). Foreign keys restrict deletion for operational history; order lines and shipment lines cascade only from their owning parent record.

| Model / table | Main fields and role |
| --- | --- |
| `Manufacturer` / `manufacturers` | `name`, `location`, contact email/phone, `created_at`; manufacturer supplying distributors. |
| `Distributor` / `distributors` | Manufacturer FK, `name`, location and contact details. A distributor is the roll-up scope for warehouses, stores, fleet, drivers, and KPIs. |
| `Warehouse` / `warehouses` | Distributor FK, name/location, required latitude/longitude, positive `storage_capacity`. Capacity uses product storage units and is enforced by a PostgreSQL trigger. |
| `Store` / `stores` | Optional unique M5 `store_id`, unique synthetic placeholder code, required `state_id`, required coordinates, name, distributor FK, and assigned warehouse FK. The assigned warehouse must belong to the same distributor. Synthetic seed coordinates are approximate locations in CA, TX and WI, not verified Walmart coordinates. |
| `Product` / `products` | Optional unique M5 `item_id`, `dept_id`, and `cat_id`; name, unit of measure, nonnegative `unit_cost`, positive `storage_units_per_item`. |
| `Truck` / `trucks` | Distributor FK, unique registration, positive capacity/fuel efficiency, optional current coordinates, availability status. |
| `Driver` / `drivers` | Distributor FK, name/contact, salary type, base salary, per-distance rate, optional current coordinates and availability. |
| `Inventory` / `inventories` | Product FK, exactly one warehouse/store FK, nonnegative on-hand/reserved/reorder values, optional maximum, `updated_at`. Reserved cannot exceed on-hand; product/location is unique. |
| `Order` / `orders` | Unique order number, type/status, explicit source/destination FKs, order/expected/actual dates. A check constraint enforces one of the three supported order flows. |
| `OrderLine` / `order_lines` | Order and product FKs, positive requested quantity, fulfilled quantity between zero and requested, nonnegative unit price and optional backorder expiry. |
| `Backorder` / `backorders` | One per order line; positive remaining quantity, expiry, and open/fulfilled/expired/cancelled status. |
| `Shipment` / `shipments` | Order, warehouse, truck, distributor, exactly one typed origin and destination, shipment status and dispatch/arrival times. Composite FKs keep truck and warehouse in the same distributor. |
| `ShipmentLine` / `shipment_lines` | Shipment and order-line FKs, positive shipped quantity, delivered quantity within shipped amount, computed in-transit amount. In-transit stock is not warehouse or store on-hand. |
| `UnmetDemand` / `unmet_demand` | Store/product/order FKs, requested, fulfilled and unmet quantities, timestamp and reason. Composite FK ties it to the order's store. |
| `Disruption` / `disruptions` | Type, time interval, severity, status and description. |
| `DisruptionTarget` / `disruption_targets` | Disruption FK and exactly one manufacturer/distributor/warehouse/store/truck FK. |
| `Trip` / `trips` | Truck, driver, shipment and distributor FKs; route descriptions, distance, estimated/actual duration, fuel, status and times. Composite FKs enforce a shared distributor across driver, truck and shipment. |
| `KPISnapshot` / `kpi_snapshots` | Distributor FK, optional same-distributor warehouse FK, date, inventory/revenue/expense/fill/stockout/unmet metrics. Generated `total_profit` subtracts all expense columns from revenue. |
| `CalendarWeek` / `calendar_weeks` | Unique M5 `wm_yr_wk` key. |
| `M5CalendarDate` / `calendar_dates` | Unique M5 `d` and date, week FK, weekday/month/year, event fields and CA/TX/WI SNAP flags. |
| `DailySalesRecord` / `daily_sales_records` | Product/store/calendar-date FKs, nonnegative `units_sold`; unique product/store/day. |
| `WeeklySellPrice` / `weekly_sell_prices` | Product/store/week FKs, nonnegative selling price; unique product/store/week. |

M5 identifiers are nullable on Product and Store until actual source IDs are available. PostgreSQL unique constraints permit multiple null values but prevent duplicate non-null external IDs.
