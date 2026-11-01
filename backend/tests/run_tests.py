"""
backend/tests/run_tests.py
Zero-dependency test runner to execute all unit & integration test suites.
"""

import sys
import os
import time
import traceback

# Ensure scm-twin root is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.tests.test_contracts import (
    test_seed_sizes_match_specification,
    test_contract_serialization,
)
from backend.tests.test_demand_transit import (
    test_demand_generator_seasonality,
    test_stochastic_lead_time_distribution,
    test_truck_breakdown_and_cluster_failover,
)
from backend.tests.test_sim_engine import (
    test_simulation_runs_and_accrues_kpis,
)
from backend.tests.test_reproducibility import (
    test_identical_seed_produces_identical_results,
    test_different_seeds_produce_variability,
    test_monte_carlo_batch_report,
)
from backend.tests.test_disruptions import (
    test_disruption_impact_and_recovery,
)
from backend.tests.test_optimizers import (
    test_demand_weighted_clustering,
    test_rebalancing_optimizer_moves_surplus_to_deficit,
    test_vrp_clarke_wright_capacity_and_2opt,
    test_dynamic_breakdown_failover_rerouting,
    test_simulation_rebalancing_reduces_unmet_demand,
)


def run_all_tests():
    test_suites = [
        ("Contracts & Seed Specs", [
            test_seed_sizes_match_specification,
            test_contract_serialization,
        ]),
        ("Demand & Stochastic Transit", [
            test_demand_generator_seasonality,
            test_stochastic_lead_time_distribution,
            test_truck_breakdown_and_cluster_failover,
        ]),
        ("Simulation Engine & SimPy Loop", [
            test_simulation_runs_and_accrues_kpis,
        ]),
        ("Seed Reproducibility", [
            test_identical_seed_produces_identical_results,
            test_different_seeds_produce_variability,
            test_monte_carlo_batch_report,
        ]),
        ("Disruption Engine & Recovery", [
            test_disruption_impact_and_recovery,
        ]),
        ("Phase 7 Optimization (Clustering, MILP, VRP, Failover)", [
            test_demand_weighted_clustering,
            test_rebalancing_optimizer_moves_surplus_to_deficit,
            test_vrp_clarke_wright_capacity_and_2opt,
            test_dynamic_breakdown_failover_rerouting,
            test_simulation_rebalancing_reduces_unmet_demand,
        ]),
    ]

    total_passed = 0
    total_failed = 0
    start_time = time.time()

    print("\n" + "=" * 65)
    print(" SCM DIGITAL TWIN - PHASE 5 SIMULATION SUITE TEST RUNNER")
    print("=" * 65 + "\n")

    for suite_name, tests in test_suites:
        print(f"Suite: {suite_name}")
        for test_fn in tests:
            t0 = time.time()
            try:
                test_fn()
                elapsed = (time.time() - t0) * 1000
                print(f"  [PASS] {test_fn.__name__} ({elapsed:.1f}ms)")
                total_passed += 1
            except Exception as e:
                elapsed = (time.time() - t0) * 1000
                print(f"  [FAIL] {test_fn.__name__} ({elapsed:.1f}ms)")
                print(f"    Error: {e}")
                traceback.print_exc()
                total_failed += 1

    total_time = time.time() - start_time
    print("\n" + "-" * 65)
    print(f"RESULTS: {total_passed} passed, {total_failed} failed in {total_time:.2f}s")
    print("-" * 65 + "\n")

    if total_failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
