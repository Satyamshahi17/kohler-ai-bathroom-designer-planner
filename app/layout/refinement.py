"""Deterministic-first layout repair with optional proposal callback."""
from __future__ import annotations

from copy import deepcopy
from collections.abc import Callable

from app.models.layout import Layout
from app.models.product import Product
from app.models.spatial_plan import SpatialPlan
from app.geometry.validator import GeometryValidator


class LayoutRefiner:
    def __init__(self, validator: GeometryValidator | None = None, max_iterations: int = 3):
        self.validator = validator or GeometryValidator()
        self.max_iterations = max(1, max_iterations)

    def refine(self, layout: Layout, products: dict[str, Product], spatial_plan: SpatialPlan | None = None,
               proposal_callback: Callable[[Layout, list[dict[str, object]]], Layout] | None = None) -> tuple[Layout, dict[str, object], int]:
        current = deepcopy(layout)
        for iteration in range(self.max_iterations + 1):
            result = self.validator.validate(current, products, spatial_plan)
            if result["valid"] or iteration == self.max_iterations:
                return current, result, iteration
            if proposal_callback:
                proposed = proposal_callback(current, result["violations"])
                current = proposed
            else:
                current = self._deterministic_repair(current, products, result["violations"], spatial_plan)
        return current, self.validator.validate(current, products, spatial_plan), self.max_iterations

    @staticmethod
    def _deterministic_repair(layout: Layout, products: dict[str, Product], violations: list[dict[str, object]], spatial_plan: SpatialPlan | None = None) -> Layout:
        repaired = deepcopy(layout)
        offending = {v.get("fixture") for v in violations if v.get("fixture")}
        for placement in repaired.fixtures:
            if placement.product_id not in offending:
                continue
            product = products.get(placement.product_id)
            if not product:
                continue
            # Try a small deterministic sequence of positions. This is a fallback
            # repair, not a substitute for the future LLM refinement proposal.
            candidates = [(20, 20), (layout.room_width - product.width - 20, 20),
                          (20, layout.room_depth - product.depth - 20),
                          (layout.room_width - product.width - 20, layout.room_depth - product.depth - 20)]
            # Pick the first position that improves the number of hard violations.
            original = (placement.x, placement.y)
            best = original
            best_count = float("inf")
            for x, y in candidates:
                placement.x, placement.y = max(0, x), max(0, y)
                trial = GeometryValidator().validate(repaired, products, spatial_plan)
                count = trial.get("hard_violation_count", 0)
                if count < best_count:
                    best_count, best = count, (placement.x, placement.y)
            placement.x, placement.y = best
        return repaired
