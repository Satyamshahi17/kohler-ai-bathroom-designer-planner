"""Deterministic evaluation metrics for the bathroom designer POC."""
from __future__ import annotations

from math import hypot
from typing import Any


def _err(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    return abs(float(a) - float(b))


def spatial_extraction_metrics(predicted: dict[str, Any], gold: dict[str, Any]) -> dict[str, Any]:
    """Compare extracted spatial fields against a gold plan without inventing missing values."""
    room_p = predicted.get("room", predicted)
    room_g = gold.get("room", gold)
    width_error = _err(room_p.get("width"), room_g.get("width"))
    depth_error = _err(room_p.get("depth"), room_g.get("depth"))

    dp = predicted.get("door") or {}
    dg = gold.get("door") or {}
    door_fields = ("offset", "width")
    door_errors = {f: _err(dp.get(f), dg.get(f)) for f in door_fields}
    exact = 0
    total = 0
    for f in ("wall", "hinge_position", "opening_direction"):
        if f in dg and dg[f] is not None:
            total += 1
            exact += int(dp.get(f) == dg[f])
    windows_p = predicted.get("windows") or []
    windows_g = gold.get("windows") or []
    window_exact = 0
    for gw in windows_g:
        found = any(
            pw.get("wall") == gw.get("wall")
            and _err(pw.get("offset"), gw.get("offset")) == 0
            and _err(pw.get("width"), gw.get("width")) == 0
            for pw in windows_p
        )
        window_exact += int(found)

    return {
        "room_width_error_mm": width_error,
        "room_depth_error_mm": depth_error,
        "door_offset_error_mm": door_errors["offset"],
        "door_width_error_mm": door_errors["width"],
        "door_categorical_accuracy": (exact / total) if total else None,
        "window_detection_accuracy": (window_exact / len(windows_g)) if windows_g else 1.0,
    }


def recommendation_metrics(bundle: dict[str, Any], *, required_categories: list[str]) -> dict[str, Any]:
    products = bundle.get("products", [])
    categories = [p.get("category") for p in products]
    missing = sorted(set(required_categories) - set(categories))
    duplicate_categories = sorted(c for c in set(categories) if categories.count(c) > 1)
    return {
        "required_category_coverage": ((len(required_categories) - len(missing)) / len(required_categories)) if required_categories else 1.0,
        "missing_categories": missing,
        "duplicate_categories": duplicate_categories,
        "compatibility_violation": bool(bundle.get("constraint_satisfaction", {}).get("compatibility") is False),
    }


def optimization_metrics(bundle: dict[str, Any], budget: float | None) -> dict[str, Any]:
    total = float(bundle.get("total_cost", 0.0))
    cs = bundle.get("constraint_satisfaction", {})
    return {
        "budget_violation": budget is not None and total > budget + 1e-9,
        "budget_shortfall": max(0.0, total - budget) if budget is not None else 0.0,
        "accessory_omission": bool(cs.get("required_accessories") is False),
        "infeasible_bundle": not bool(bundle.get("budget_feasible", True)) and budget is not None and total <= budget,
    }


def layout_metrics(validation: dict[str, Any], *, repair_attempted: bool = False, repair_succeeded: bool = False) -> dict[str, Any]:
    violations = validation.get("violations", []) or []
    counts: dict[str, int] = {}
    for v in violations:
        key = str(v.get("type", "UNKNOWN")).lower()
        counts[key] = counts.get(key, 0) + 1
    return {
        "valid": bool(validation.get("valid")),
        "fixture_overlap_violation": counts.get("collision", 0) > 0,
        "room_boundary_violation": counts.get("out_of_bounds", 0) > 0,
        "door_swing_violation": counts.get("door_swing", 0) > 0,
        "clearance_violation": counts.get("clearance", 0) > 0,
        "circulation_violation": counts.get("circulation", 0) > 0,
        "infrastructure_violation": counts.get("infrastructure", 0) > 0,
        "repair_attempted": repair_attempted,
        "repair_succeeded": repair_succeeded,
    }


def aggregate_design_metrics(*, spatial: dict[str, Any] | None, recommendation: dict[str, Any],
                             optimization: dict[str, Any], layout: dict[str, Any]) -> dict[str, Any]:
    return {
        "spatial_extraction": spatial or {},
        "recommendation": recommendation,
        "optimization": optimization,
        "layout": layout,
        "fully_valid_design": bool(
            layout.get("valid")
            and not optimization.get("budget_violation")
            and not optimization.get("accessory_omission")
            and not recommendation.get("compatibility_violation")
            and recommendation.get("required_category_coverage", 0) == 1.0
        ),
    }
