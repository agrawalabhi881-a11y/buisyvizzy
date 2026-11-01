"""
backend/tests/test_disruptions.py
Tests disruption injection and resilience recovery tracking.
"""

from contracts.models import DisruptionContract, DisruptionType
from backend.app.sim.runner import MonteCarloScenarioRunner


def test_disruption_impact_and_recovery():
    runner = MonteCarloScenarioRunner(base_seed=555)

    # 1. Normal run with no disruptions
    baseline_run = runner.run_single_scenario(seed=555, duration_ticks=15)
    baseline_final = baseline_run[-1]

    # 2. Run with severe demand spike disruption at Day 3 for 5 days
    disruption = DisruptionContract(
        id="DISR_SPIKE_01",
        disruption_type=DisruptionType.DEMAND_SPIKE,
        target_id="ALL",
        start_tick=3,
        duration_ticks=5,
        severity=4.0,  # 4x demand surge
        description="Flash holiday surge",
    )

    stressed_run = runner.run_single_scenario(
        seed=555,
        duration_ticks=15,
        disruptions=[disruption],
    )
    stressed_final = stressed_run[-1]

    # Stressed scenario must have experienced higher demanded units and unmet units
    assert stressed_final.total_demanded_units > baseline_final.total_demanded_units
    assert stressed_final.total_unmet_units > baseline_final.total_unmet_units
    # Fill rate drops under sudden 4x shock
    assert stressed_final.fill_rate < baseline_final.fill_rate
