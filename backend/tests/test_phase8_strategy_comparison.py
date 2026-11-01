"""
backend/tests/test_phase8_strategy_comparison.py
Unit and integration tests for Phase 8: Disruption Scenarios & Strategy Comparison.
Tests 5 canonical scenarios, paired Monte Carlo evaluation under CRN,
Student's t p-values, 95% Confidence Intervals, and REST API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

try:
    from app.main import app
    from app.sim.strategy_comparison import (
        ScenarioType,
        DisruptionScenarioRegistry,
        StrategyComparisonEvaluator,
    )
    from app.services.auth_service import create_access_token
except ImportError:
    from backend.app.main import app
    from backend.app.sim.strategy_comparison import (
        ScenarioType,
        DisruptionScenarioRegistry,
        StrategyComparisonEvaluator,
    )
    from backend.app.services.auth_service import create_access_token


client = TestClient(app)


def test_scenario_registry_coverage():
    """Validates that all 5 required scenarios are registered with valid disruptions."""
    scenarios = list(ScenarioType)
    assert len(scenarios) == 5
    assert ScenarioType.BASELINE_STEADY_STATE in scenarios
    assert ScenarioType.SEVERE_SUPPLIER_FAILURE in scenarios
    assert ScenarioType.REGIONAL_DEMAND_SPIKE in scenarios
    assert ScenarioType.TRANSPORTATION_LANE_SHUTDOWN in scenarios
    assert ScenarioType.COMPOUND_BLACK_SWAN in scenarios

    # Check compound black swan has 3 distinct disruption vectors
    black_swan = DisruptionScenarioRegistry.get_disruptions(ScenarioType.COMPOUND_BLACK_SWAN)
    assert len(black_swan) == 3

    # Check steady state has 0 disruptions
    steady = DisruptionScenarioRegistry.get_disruptions(ScenarioType.BASELINE_STEADY_STATE)
    assert len(steady) == 0


def test_paired_monte_carlo_crn_and_significance():
    """Validates paired evaluation under Common Random Numbers (CRN) with statistical significance."""
    evaluator = StrategyComparisonEvaluator(base_seed=2000)
    report = evaluator.evaluate_scenario(
        scenario_type=ScenarioType.REGIONAL_DEMAND_SPIKE,
        num_seeds=3,
        duration_ticks=15,
    )

    assert report.scenario_type == ScenarioType.REGIONAL_DEMAND_SPIKE
    assert report.num_paired_seeds == 3
    assert report.duration_ticks == 15

    # Check all key metrics are populated
    for metric_key in ["total_operating_cost", "fill_rate", "unmet_demand_units", "stockout_frequency"]:
        assert metric_key in report.metrics
        m = report.metrics[metric_key]
        assert isinstance(m.baseline_mean, float)
        assert isinstance(m.optimized_mean, float)
        assert isinstance(m.p_value, float)
        assert 0.0 <= m.p_value <= 1.0
        assert m.ci_95_lower <= m.ci_95_upper

    # Check recovery timeline length
    assert len(report.recovery_timeline) == 15
    assert report.recovery_timeline[0].tick == 0
    assert report.recovery_timeline[-1].tick == 14

    # Check key findings and verdict
    assert len(report.key_findings) > 0
    assert "Optimized Strategy" in report.verdict


def test_scenario_catalog_endpoint():
    """Tests GET /api/simulation/scenarios/catalog endpoint."""
    res = client.get("/api/simulation/scenarios/catalog")
    assert res.status_code == 200
    data = res.json()
    assert "catalog" in data
    assert len(data["catalog"]) == 5
    types = [item["scenario_type"] for item in data["catalog"]]
    assert "COMPOUND_BLACK_SWAN" in types


def test_strategy_comparison_api_endpoint():
    """Tests POST /api/simulation/strategy-comparison with RBAC."""
    admin_token = create_access_token({"sub": "admin1", "role": "ADMIN"})
    driver_token = create_access_token({"sub": "driver1", "role": "TRUCK_DRIVER"})

    # 1. Driver should be forbidden
    res_forbidden = client.post(
        "/api/simulation/strategy-comparison",
        json={"scenario_type": "REGIONAL_DEMAND_SPIKE", "num_seeds": 2, "duration_ticks": 10},
        headers={"Authorization": f"Bearer {driver_token}"},
    )
    assert res_forbidden.status_code == 403

    # 2. Admin can run strategy comparison
    res_run = client.post(
        "/api/simulation/strategy-comparison",
        json={"scenario_type": "REGIONAL_DEMAND_SPIKE", "num_seeds": 2, "duration_ticks": 10},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_run.status_code == 200
    report = res_run.json()
    assert report["scenario_type"] == "REGIONAL_DEMAND_SPIKE"
    assert "metrics" in report
    assert "unmet_demand_units" in report["metrics"]
    assert len(report["recovery_timeline"]) == 10
