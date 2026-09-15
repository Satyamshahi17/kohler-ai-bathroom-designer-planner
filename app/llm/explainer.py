"""Optional explanation generation; deterministic fallback keeps the POC usable offline."""
from __future__ import annotations

from typing import Any


def explain_design(constraints: dict[str, Any], bundle: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary": "The design prioritizes explicit user requirements, product compatibility, budget, and deterministic spatial feasibility.",
        "theme": constraints.get("theme", ""),
        "budget": constraints.get("budget"),
        "total_cost": bundle.get("total_cost"),
        "budget_feasible": bundle.get("budget_feasible"),
        "hard_geometry_valid": validation.get("valid", False),
    }
