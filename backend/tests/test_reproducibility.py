"""
backend/tests/test_reproducibility.py
Verifies that the simulation is 100% reproducible given a fixed seed.
Key judging requirement for fair, paired strategy comparisons.
"""

from backend.app.sim.runner import MonteCarloScenarioRunner


def test_identical_seed_produces_identical_results():
    runner = MonteCarloScenarioRunner(base_seed=42)

    run_1 = runner.run_single_scenario(seed=42, duration_ticks=10)
    run_2 = runner.run_single_scenario(seed=42, duration_ticks=10)

    snap1 = run_1[-1]
    snap2 = run_2[-1]

    # Exact bit-for-bit equivalence
    assert snap1.total_revenue == snap2.total_revenue
    assert snap1.total_operating_cost == snap2.total_operating_cost
    assert snap1.total_demanded_units == snap2.total_demanded_units
    assert snap1.total_fulfilled_units == snap2.total_fulfilled_units
    assert snap1.total_unmet_units == snap2.total_unmet_units
    assert snap1.fill_rate == snap2.fill_rate


def test_different_seeds_produce_variability():
    runner = MonteCarloScenarioRunner(base_seed=100)

    run_1 = runner.run_single_scenario(seed=101, duration_ticks=10)
    run_2 = runner.run_single_scenario(seed=999, duration_ticks=10)

    snap1 = run_1[-1]
    snap2 = run_2[-1]

    # Stochastic variance should cause total demand or costs to differ
    assert snap1.total_demanded_units != snap2.total_demanded_units


def test_monte_carlo_batch_report():
    runner = MonteCarloScenarioRunner(base_seed=200)
    report = runner.run_monte_carlo_batch(
        strategy_name="Baseline (s, S)",
        num_seeds=5,
        duration_ticks=10,
    )
    assert report.num_runs == 5
    assert report.avg_total_cost > 0.0
    assert 0.0 <= report.avg_fill_rate <= 1.0
    assert report.ci_95_total_cost >= 0.0
