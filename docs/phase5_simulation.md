# Phase 5: Discrete-Event Simulation Engine

The core discrete-event simulation engine for the **AI-Powered Supply Chain Digital Twin** is built with **SimPy**, **NumPy**, and **Pydantic**. It runs entirely in memory without database dependencies, allowing rapid scenario execution and decoupled development.

---

## 1. Directory Structure

```
scm-twin/
  contracts/
    __init__.py
    models.py              # Pydantic v2 data contracts (Nodes, Trucks, Orders, Shipments, KPIs)
    seed_specs.py          # Deterministic seed network (1 Mfr, 2 Dist, 3 WH, 20 Stores, 50 Products, 10 Trucks)
  backend/
    app/
      sim/
        __init__.py
        engine.py          # SimPy simulation engine implementing the canonical Diagram 3 tick loop
        demand.py          # Stochastic demand generator (Poisson + DOW seasonality, historical replay, quantile sampling)
        transit.py         # Stochastic transit lead-times (lognormal heavy-tail) & truck cluster failover
        policy.py          # Baseline (s, S) replenishment policy
        disruptions.py     # Disruption injection engine (supplier failure, demand spike, transit delay)
        kpi.py             # Real-time financial & operational KPI accrual
        network.py         # In-memory graph state with haversine distance calculations
        runner.py          # Multi-seed Monte Carlo batch runner with 95% confidence intervals
    tests/
      test_contracts.py
      test_demand_transit.py
      test_sim_engine.py
      test_reproducibility.py
      test_disruptions.py
      run_tests.py         # Zero-dependency test runner
    demo_sim.py            # Interactive 14-day simulation CLI demo
```

---

## 2. Canonical Tick Execution Flow (Diagram 3)

Every simulation step (`run_tick()` / `sim_process`) executes the 9 canonical stages:

1. **Clock Advance ($t$):** Steps forward to day $t$.
2. **Disruption Injection:** Activates/expires disruptions scheduled by Admin.
3. **Inbound Delivery:** Checks shipments where `arrival_tick <= t`, updates inventory, and frees trucks back to `IDLE`.
4. **Demand Generation:** Generates customer demand per store/product with day-of-week seasonality and active demand spikes.
5. **Store Order Placement:** Stores emit orders to their geographically assigned warehouse.
6. **Warehouse Fulfillment:** Checks inventory, fulfills available stock, logs **UnmetDemand** penalties on stockouts, samples internal handling lead time, and dispatches trucks.
7. **Distributor Replenishment:** Evaluates baseline $(s, S)$ reorder points and orders upstream from the Manufacturer when aggregate inventory position $\le s$.
8. **Logistics & Failover:** Simulates truck movement with stochastic delays and triggers dynamic rerouting to the nearest idle truck in the same spatial cluster upon mechanical breakdown.
9. **KPI Accrual & Snapshot:** Computes daily revenue, holding cost, transport cost, driver salaries, unmet demand penalties, fill rate, and stockout frequency.

---

## 3. How to Run

### Run the Full Test Suite:
```bash
python backend/tests/run_tests.py
```

### Run the Interactive Live Demo:
```bash
python backend/demo_sim.py
```
