import json
from pathlib import Path

from app.evaluation.metrics import layout_metrics, optimization_metrics, recommendation_metrics, spatial_extraction_metrics
from app.evaluation.scenarios import scenarios, load_spatial_plan


def test_all_benchmark_scenarios_have_gold_files():
    for scenario in scenarios():
        assert scenario.plan_path.exists()
        assert scenario.gold_path.exists()


def test_spatial_metrics_exact_gold():
    scenario = scenarios()[0]
    plan = json.loads(scenario.plan_path.read_text())
    gold = json.loads(scenario.gold_path.read_text())
    predicted = {"room": plan["room"], "door": plan["door"], "windows": plan["windows"]}
    metrics = spatial_extraction_metrics(predicted, gold)
    assert metrics["room_width_error_mm"] == 0
    assert metrics["room_depth_error_mm"] == 0
    assert metrics["door_width_error_mm"] == 0
    assert metrics["window_detection_accuracy"] == 1


def test_missing_dimensions_do_not_create_fake_error():
    scenario = next(s for s in scenarios() if "missing_dimensions" in s.id)
    plan = load_spatial_plan(scenario.plan_path)
    assert plan.room_width.value is None
    assert plan.room_depth.value is None


def test_layout_metrics_classify_violations():
    result = layout_metrics({"valid": False, "violations": [
        {"type": "COLLISION"}, {"type": "DOOR_SWING"}, {"type": "CLEARANCE"},
    ]})
    assert result["fixture_overlap_violation"]
    assert result["door_swing_violation"]
    assert result["clearance_violation"]


def test_budget_metric_includes_shortfall():
    result = optimization_metrics({"total_cost": 1200, "budget_feasible": False, "constraint_satisfaction": {}}, 1000)
    assert result["budget_violation"]
    assert result["budget_shortfall"] == 200


def test_recommendation_category_coverage():
    result = recommendation_metrics({"products": [{"category": "vanity"}]}, required_categories=["vanity", "toilet"])
    assert result["required_category_coverage"] == 0.5
    assert result["missing_categories"] == ["toilet"]
