"""Validate, refine, score and select the best layout."""
from __future__ import annotations

from app.models.layout import Layout
from app.models.product import Product
from app.models.spatial_plan import SpatialPlan
from app.geometry.validator import GeometryValidator
from .refinement import LayoutRefiner
from .scorer import LayoutScorer


class LayoutSelector:
    def __init__(self, validator=None, refiner=None, scorer=None):
        self.validator = validator or GeometryValidator()
        self.refiner = refiner or LayoutRefiner(self.validator)
        self.scorer = scorer or LayoutScorer()

    def select(self, candidates: list[Layout], products: dict[str, Product],
               spatial_plan: SpatialPlan | None = None, theme: str = "",
               preferences: list[str] | None = None) -> dict[str, object]:
        evaluated = []
        for candidate in candidates:
            validation = self.validator.validate(candidate, products, spatial_plan)
            refinement_iterations = 0
            refined = candidate
            if not validation["valid"]:
                refined, validation, refinement_iterations = self.refiner.refine(candidate, products, spatial_plan)
            score = self.scorer.score(refined, validation, theme, preferences)
            evaluated.append({"layout": refined, "validation": validation,
                              "score": score, "refinement_iterations": refinement_iterations})
        valid = [item for item in evaluated if item["validation"]["valid"]]
        best = max(valid, key=lambda item: item["score"]["total"]) if valid else None
        return {"best": best, "candidates": evaluated, "valid_count": len(valid),
                "total_count": len(evaluated), "all_valid": bool(valid)}
