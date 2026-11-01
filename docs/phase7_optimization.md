# Phase 7: Optimization Engine (MILP Rebalancing, Clustering, VRP & Dynamic Failover)

The Phase 7 optimization engine provides the algorithmic intelligence that proves **predictive insights change operational actions**.

---

## 1. Modules Implemented

### 1.1 Spatial & Demand Clustering (`backend/app/optimizers/clustering.py`)
- **Algorithm:** Demand-Weighted K-Means++ with Lloyds heuristic.
- **Function:** Groups 20 retail stores into 3 geographic delivery clusters (Northeast, Midwest, Southeast) weighted by store consumer demand volume.
- **Output:** Cluster centroids, bounding boxes, store assignments, and cluster aggregate demands.

### 1.2 Multi-Warehouse Inventory Rebalancing (`backend/app/optimizers/rebalance.py`)
- **Algorithm:** Mixed-Integer Linear Program / Primal-Dual Transportation Optimizer.
- **Objective Function:**
  $$\max \sum_{i \ne j} \sum_p (\text{Penalty}_p - \text{FreightCost}_{i,j}) \cdot x_{i,j,p}$$
- **Constraints:**
  - Origin surplus limitation: $\sum_{j} x_{i,j,p} \le \text{Surplus}_{i,p} = \max(0, I_{i,p} - \text{SafetyStock}_{i,p})$
  - Destination deficit limitation: $\sum_{i} x_{i,j,p} \le \text{Deficit}_{j,p} = \max(0, \text{ReorderPoint}_{j,p} - I_{j,p})$
  - Destination warehouse maximum physical capacity limit
  - Positive marginal economic gain filter (only executes transfers where Penalty Avoided $>$ Transit Freight Cost).
- **Output:** Transfer manifest with origin, destination, quantity, estimated transit cost, penalty avoided, and net benefit.

### 1.3 Capacitated Vehicle Routing Problem (CVRP) (`backend/app/optimizers/vrp.py`)
- **Algorithm:** Clarke-Wright Savings Heuristic + 2-Opt Edge-Swap Local Search.
- **Function:** Solves multi-stop truck routes departing from the cluster warehouse to assigned stores.
- **Constraints:** Truck payload capacity ($C = 600$ units), driver shift limits, return-to-depot tours.
- **Output:** Stop sequences, arrival orders, cumulative distance, transit hours, fuel burn, and driver salary allocation.

### 1.4 Dynamic Breakdown Failover & Real-Time Rerouting (`backend/app/optimizers/failover.py`)
- **Algorithm:** Nearest Idle Cluster Asset Recovery.
- **Function:** If a truck breaks down mid-route, detects remaining unvisited delivery stops, finds the nearest idle truck in the same spatial cluster, and re-solves a sub-VRP to rescue the cargo with an added transit penalty.

---

## 2. Common Random Numbers (CRN) Synchronization

To ensure statistically valid, fair comparisons between the Baseline and Optimized strategies, the demand generator and transit engine use **independent, synchronized RNG seeds**:
- Both policies experience identical customer demand series.
- Differences in service levels, stockouts, and penalties are purely attributable to the optimizer.

---

## 3. How to Run

### Run Full Test Suite (15 Tests):
```bash
python backend/tests/run_tests.py
```

### Run Comparative Optimization Benchmark:
```bash
python backend/demo_optimization_comparison.py
```
*(Or run `.\run_optimization_demo.ps1` / `run_optimization_demo.bat`)*
