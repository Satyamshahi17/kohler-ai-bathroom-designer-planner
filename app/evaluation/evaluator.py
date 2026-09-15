"""Benchmark runner for the bathroom designer POC."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from app.evaluation.metrics import aggregate_design_metrics, layout_metrics, optimization_metrics, recommendation_metrics, spatial_extraction_metrics
from app.evaluation.scenarios import EvaluationScenario, load_spatial_plan, scenarios


class Evaluator:
    def __init__(self, pipeline, *, output_dir: str | Path | None = None):
        self.pipeline = pipeline
        self.output_dir = Path(output_dir or Path(__file__).resolve().parents[2] / "evaluation" / "benchmark_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def evaluate_scenario(self, scenario: EvaluationScenario) -> dict[str, Any]:
        plan = load_spatial_plan(scenario.plan_path)
        result = self.pipeline.run(requirements=scenario.requirements, constraints=None, spatial_plan=plan)
        gold = json.loads(scenario.gold_path.read_text(encoding="utf-8"))

        predicted = {
            "room": {"width": plan.room_width.value, "depth": plan.room_depth.value},
            "door": {
                "wall": plan.door.wall if plan.door else None,
                "offset": plan.door.offset.value if plan.door and plan.door.offset else None,
                "width": plan.door.width.value if plan.door and plan.door.width else None,
                "hinge_position": plan.door.hinge_position if plan.door else None,
                "opening_direction": plan.door.opening_direction if plan.door else None,
            },
            "windows": plan.windows,
        }
        spatial = spatial_extraction_metrics(predicted, gold)
        rec = recommendation_metrics(result.bundle, required_categories=list(scenario.required_categories))
        opt = optimization_metrics(result.bundle, scenario.budget)
        lay = layout_metrics(result.validation, repair_attempted=any(t.get("stage") == "layout_refinement" for t in result.trace), repair_succeeded=result.status == "success")
        aggregate = aggregate_design_metrics(spatial=spatial, recommendation=rec, optimization=opt, layout=lay)

        return {
            "scenario": asdict(scenario) | {"plan_path": str(scenario.plan_path), "gold_path": str(scenario.gold_path)},
            "status": result.status,
            "metrics": aggregate,
            "trace": result.trace,
            "bundle": result.bundle,
            "validation": result.validation,
        }

    def run(self, selected: list[EvaluationScenario] | None = None) -> dict[str, Any]:
        results = [self.evaluate_scenario(s) for s in (selected or scenarios())]
        summary = self._summarize(results)
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "scenario_count": len(results),
            "summary": summary,
            "scenarios": results,
        }
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = self.output_dir / f"benchmark_{stamp}.json"
        path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        (self.output_dir / "latest.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        return report

    @staticmethod
    def _summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
        n = len(results) or 1
        m = [r["metrics"] for r in results]
        layout = [x["layout"] for x in m]
        rec = [x["recommendation"] for x in m]
        opt = [x["optimization"] for x in m]
        spatial = [x["spatial_extraction"] for x in m]
        fully_valid = sum(x["fully_valid_design"] for x in m)
        return {
            "fully_valid_design_rate": fully_valid / n,
            "average_layout_validity": sum(x["valid"] for x in layout) / n,
            "fixture_overlap_violation_rate": sum(x["fixture_overlap_violation"] for x in layout) / n,
            "room_boundary_violation_rate": sum(x["room_boundary_violation"] for x in layout) / n,
            "door_swing_violation_rate": sum(x["door_swing_violation"] for x in layout) / n,
            "clearance_violation_rate": sum(x["clearance_violation"] for x in layout) / n,
            "circulation_violation_rate": sum(x["circulation_violation"] for x in layout) / n,
            "infrastructure_violation_rate": sum(x["infrastructure_violation"] for x in layout) / n,
            "budget_violation_rate": sum(x["budget_violation"] for x in opt) / n,
            "accessory_omission_rate": sum(x["accessory_omission"] for x in opt) / n,
            "compatibility_violation_rate": sum(x["compatibility_violation"] for x in rec) / n,
            "required_category_coverage": sum(x["required_category_coverage"] for x in rec) / n,
            "room_width_mae_mm": _mean_non_null(spatial, "room_width_error_mm"),
            "room_depth_mae_mm": _mean_non_null(spatial, "room_depth_error_mm"),
            "door_width_mae_mm": _mean_non_null(spatial, "door_width_error_mm"),
            "door_offset_mae_mm": _mean_non_null(spatial, "door_offset_error_mm"),
            "window_detection_accuracy": sum(x["window_detection_accuracy"] for x in spatial) / n,
            "repair_success_rate": sum(x["repair_succeeded"] for x in layout if x["repair_attempted"]) / max(1, sum(x["repair_attempted"] for x in layout)),
        }


def _mean_non_null(items, key):
    values = [x[key] for x in items if x.get(key) is not None]
    return sum(values) / len(values) if values else None
