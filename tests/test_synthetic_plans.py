import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLANS = ROOT / "evaluation" / "bathroom_plans"
GOLD = ROOT / "evaluation" / "expected_outputs"


def test_expected_evaluation_plans_exist():
    plans = sorted(PLANS.glob("plan_*.json"))
    gold = sorted(GOLD.glob("plan_*_gold.json"))
    assert len(plans) == 6
    assert len(gold) == 6


def test_missing_dimension_case_is_explicit():
    data = json.loads((PLANS / "plan_05_missing_dimensions.json").read_text())
    assert data["room"]["width"] is None
    assert data["room"]["depth"] is None


def test_unknown_swing_case_is_explicit():
    data = json.loads((PLANS / "plan_06_unknown_door_swing.json").read_text())
    assert data["door"]["swing_angle"] is None
