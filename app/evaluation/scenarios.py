"""Benchmark scenarios for deterministic evaluation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from app.models.spatial_plan import SpatialPlan, SourcedValue, Door, DoorSwing

ROOT = Path(__file__).resolve().parents[2]
PLAN_DIR = ROOT / "evaluation" / "bathroom_plans"
GOLD_DIR = ROOT / "evaluation" / "expected_outputs"


@dataclass(frozen=True)
class EvaluationScenario:
    id: str
    plan_path: Path
    gold_path: Path
    requirements: str
    budget: float = 5000
    required_categories: tuple[str, ...] = ("vanity", "faucet", "toilet", "shower")


def _sourced(value, unit="mm", source="user_provided", confidence=1.0):
    return SourcedValue(value=value, unit=unit, source=source, confidence=confidence)


def load_spatial_plan(path: Path) -> SpatialPlan:
    raw = json.loads(path.read_text(encoding="utf-8"))
    room = raw.get("room", {})
    door_raw = raw.get("door")
    door = None
    if door_raw:
        door = Door(
            wall=door_raw.get("wall"),
            offset=_sourced(door_raw.get("offset")) if door_raw.get("offset") is not None else None,
            width=_sourced(door_raw.get("width")) if door_raw.get("width") is not None else None,
            hinge_position=door_raw.get("hinge_position"),
            opening_direction=door_raw.get("opening_direction"),
            swing=DoorSwing(
                direction=door_raw.get("opening_direction"),
                angle=_sourced(door_raw.get("swing_angle"), "deg") if door_raw.get("swing_angle") is not None else None,
                swing_radius=_sourced(door_raw.get("swing_radius")) if door_raw.get("swing_radius") is not None else None,
            ),
        )
    return SpatialPlan(
        room_width=_sourced(room.get("width"), room.get("unit", "mm")) if room.get("width") is not None else _sourced(None, room.get("unit", "mm"), "unknown", 0),
        room_depth=_sourced(room.get("depth"), room.get("unit", "mm")) if room.get("depth") is not None else _sourced(None, room.get("unit", "mm"), "unknown", 0),
        walls=[], door=door, windows=raw.get("windows", []), ventilation=raw.get("ventilation", []),
        fixed_obstacles=raw.get("fixed_obstacles", []), existing_plumbing=raw.get("existing_plumbing", []),
        existing_electrical=raw.get("existing_electrical", []), proposed_plumbing=raw.get("proposed_plumbing", []),
        proposed_electrical=raw.get("proposed_electrical", []),
    )


def scenarios() -> list[EvaluationScenario]:
    return [
        EvaluationScenario("plan_01_small_south_door", PLAN_DIR / "plan_01_small_south_door.json", GOLD_DIR / "plan_01_small_south_door_gold.json", "Japanese Zen bathroom with vanity, faucet, toilet and shower under $5000.", 5000),
        EvaluationScenario("plan_02_medium_north_door", PLAN_DIR / "plan_02_medium_north_door.json", GOLD_DIR / "plan_02_medium_north_door_gold.json", "Warm minimalist bathroom with vanity, faucet, toilet and shower under $5000.", 5000),
        EvaluationScenario("plan_03_large_east_door", PLAN_DIR / "plan_03_large_east_door.json", GOLD_DIR / "plan_03_large_east_door_gold.json", "Spa-like modern bathroom with vanity, faucet, toilet and shower under $5000.", 5000),
        EvaluationScenario("plan_04_tiny_infeasible", PLAN_DIR / "plan_04_tiny_infeasible.json", GOLD_DIR / "plan_04_tiny_infeasible_gold.json", "Compact Japanese Zen bathroom with vanity, faucet, toilet and shower under $5000.", 5000),
        EvaluationScenario("plan_05_missing_dimensions", PLAN_DIR / "plan_05_missing_dimensions.json", GOLD_DIR / "plan_05_missing_dimensions_gold.json", "Minimal bathroom with vanity, faucet, toilet and shower under $5000.", 5000),
        EvaluationScenario("plan_06_unknown_door_swing", PLAN_DIR / "plan_06_unknown_door_swing.json", GOLD_DIR / "plan_06_unknown_door_swing_gold.json", "Warm minimalist bathroom with vanity, faucet, toilet and shower under $5000.", 5000),
    ]
