"""End-to-end orchestration for the Kohler AI Bathroom Designer."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config.settings import settings
from app.geometry.validator import GeometryValidator
from app.layout.candidate_generator import LayoutCandidateGenerator
from app.layout.selector import LayoutSelector
from app.llm.requirements import RequirementsParser
from app.llm.vision import SpatialExtractor, validate_spatial_payload
from app.models.result import DesignResult
from app.models.spatial_plan import SpatialPlan
from app.optimization.optimizer import BundleOptimizer
from app.products.catalog import load_products
from app.products.embeddings import ProductEmbeddingIndex
from app.recommendation.hybrid_ranker import HybridRanker
from app.rendering.svg_renderer import SVGRenderer


class DesignPipeline:
    """Coordinate pipeline stages while keeping each stage independently testable."""

    def __init__(self, *, catalog=None, embeddings=None, kg=None, requirements_parser=None,
                 spatial_extractor=None, optimizer=None, layout_generator=None,
                 layout_selector=None, renderer=None):
        self.catalog = catalog or load_products()
        self.products = {p.id: p for p in self.catalog}
        self.embeddings = embeddings or ProductEmbeddingIndex(self.catalog)
        self.kg = kg
        self.requirements_parser = requirements_parser or RequirementsParser()
        self.spatial_extractor = spatial_extractor or SpatialExtractor()
        self.optimizer = optimizer or BundleOptimizer(self.catalog)
        self.layout_generator = layout_generator or LayoutCandidateGenerator(candidate_count=4)
        self.layout_selector = layout_selector or LayoutSelector()
        self.renderer = renderer or SVGRenderer()

    def run(self, *, requirements: str | None = None, constraints=None,
            image_path: str | Path | None = None, spatial_plan: SpatialPlan | None = None,
            top_k: int = 3) -> DesignResult:
        trace: list[dict[str, Any]] = []
        try:
            if constraints is None:
                if not requirements:
                    raise ValueError("Requirements are required")
                constraints = self.requirements_parser.parse(requirements)
            trace.append({"stage": "requirements", "status": "success", "constraints": constraints.model_dump()})

            extraction = None
            if spatial_plan is None:
                if not image_path:
                    raise ValueError("A bathroom image or structured spatial_plan is required")
                extraction = self.spatial_extractor.extract(image_path)
                spatial_plan = extraction.spatial_plan
                trace.append({"stage": "spatial_extraction", "status": "success",
                              "exact_layout_ready": extraction.exact_layout_ready,
                              "provisional_reasons": extraction.provisional_reasons,
                              "warnings": extraction.warnings})
            else:
                trace.append({"stage": "spatial_extraction", "status": "provided",
                              "exact_layout_ready": spatial_plan.room_width.value is not None and spatial_plan.room_depth.value is not None})

            if spatial_plan.room_width.value is None or spatial_plan.room_depth.value is None:
                return DesignResult(status="provisional", spatial_plan=spatial_plan,
                                    validation={"valid": False, "reason": "Room dimensions are required for layout generation"},
                                    trace=trace)

            ranker = HybridRanker(self.catalog, self.embeddings, self.kg)
            ranked = ranker.rank(constraints)
            ranked = ranker.filter_compatible(ranked)
            trace.append({"stage": "recommendation", "status": "success",
                          "candidate_counts": {k: len(v) for k, v in ranked.items()}})

            incompatible = []
            if self.kg:
                try:
                    rows = self.kg.get_incompatible_pairs()
                    for row in rows:
                        a = row.get("a") or row.get("product_a") or row.get("source")
                        b = row.get("b") or row.get("product_b") or row.get("target")
                        if a and b:
                            incompatible.append((a, b))
                except Exception as exc:
                    trace.append({"stage": "kg_incompatibilities", "status": "degraded", "message": str(exc)})

            bundles = self.optimizer.optimize(ranked, constraints.budget, top_k=top_k,
                                              incompatible_pairs=incompatible)
            if not bundles:
                raise ValueError("No compatible product bundle could be produced")
            bundle_dicts = [b.as_dict() for b in bundles]
            trace.append({"stage": "optimization", "status": "success", "bundle_count": len(bundles),
                          "budget": constraints.budget, "totals": [b.total_cost for b in bundles]})

            primary = bundle_dicts[0]
            candidates = self.layout_generator.generate(spatial_plan, self.products, primary)
            trace.append({"stage": "layout_generation", "status": "success", "candidate_count": len(candidates)})
            selected = self.layout_selector.select(candidates, self.products, spatial_plan,
                                                   constraints.theme, constraints.preferences)
            trace.append({"stage": "layout_validation", "status": "success",
                          "valid_count": selected["valid_count"], "total_count": selected["total_count"]})
            best = selected.get("best")
            if best is None:
                return DesignResult(status="no_valid_layout", spatial_plan=spatial_plan,
                                    bundle=primary, alternatives=bundle_dicts,
                                    validation={"valid": False, "candidates": selected["candidates"]}, trace=trace)

            layout = best["layout"]
            validation = best["validation"]
            svg = self.renderer.render(layout, self.products, spatial_plan)
            explanation = self._explain(constraints, primary, layout, validation, selected)
            trace.append({"stage": "rendering", "status": "success", "svg_deterministic": True})
            return DesignResult(status="success", spatial_plan=spatial_plan, bundle=primary,
                                alternatives=bundle_dicts, layout=layout, svg=svg,
                                validation=validation, explanation=explanation, trace=trace)
        except Exception as exc:
            trace.append({"stage": "pipeline", "status": "error", "error_type": type(exc).__name__, "message": str(exc)})
            return DesignResult(status="error", spatial_plan=spatial_plan, trace=trace,
                                validation={"valid": False, "error": str(exc)})

    def replace_product(self, *, current_result: DesignResult, category: str,
                        requirements: str | None = None, constraints=None,
                        spatial_plan: SpatialPlan | None = None) -> DesignResult:
        """Replace one category and rerun only the affected recommendation-to-layout flow.

        The optimizer is rerun because accessories, budget and compatibility can change;
        layout is then regenerated from the resulting bundle. Unaffected source inputs are reused.
        """
        if constraints is None:
            if not requirements:
                raise ValueError("Requirements or constraints are required for replacement")
            constraints = self.requirements_parser.parse(requirements)
        if category not in constraints.required_categories:
            raise ValueError(f"Category {category!r} is not a required fixture category")
        plan = spatial_plan or current_result.spatial_plan
        if plan is None:
            raise ValueError("Spatial plan is required for product replacement")

        ranker = HybridRanker(self.catalog, self.embeddings, self.kg)
        ranked = ranker.filter_compatible(ranker.rank(constraints))
        current_ids = set(current_result.bundle.get("product_ids", []))
        alternatives = [r for r in ranked.get(category, []) if r.product.id not in current_ids]
        if not alternatives:
            return DesignResult(status="error", spatial_plan=plan,
                                validation={"valid": False, "error": f"No replacement products available for {category}"},
                                trace=[{"stage": "replacement", "status": "error", "category": category}])

        # Prefer an alternative product, then retain the strongest candidates from other categories.
        altered = {k: list(v) for k, v in ranked.items()}
        altered[category] = alternatives
        bundles = self.optimizer.optimize(altered, constraints.budget, top_k=3)
        if not bundles:
            raise ValueError("Replacement produced no feasible bundle")
        primary = bundles[0].as_dict()
        candidates = self.layout_generator.generate(plan, self.products, primary)
        selected = self.layout_selector.select(candidates, self.products, plan, constraints.theme, constraints.preferences)
        best = selected.get("best")
        trace = [{"stage": "replacement", "status": "success", "category": category,
                  "replaced_from": sorted(current_ids), "replacement_candidates": [r.product.id for r in alternatives[:5]]},
                 {"stage": "optimization", "status": "success", "bundle_count": len(bundles)},
                 {"stage": "layout_validation", "status": "success", "valid_count": selected["valid_count"]}]
        if best is None:
            return DesignResult(status="no_valid_layout", spatial_plan=plan, bundle=primary,
                                alternatives=[b.as_dict() for b in bundles],
                                validation={"valid": False, "candidates": selected["candidates"]}, trace=trace)
        layout = best["layout"]
        validation = best["validation"]
        svg = self.renderer.render(layout, self.products, plan)
        explanation = self._explain(constraints, primary, layout, validation, selected)
        return DesignResult(status="success", spatial_plan=plan, bundle=primary,
                            alternatives=[b.as_dict() for b in bundles], layout=layout, svg=svg,
                            validation=validation, explanation=explanation, trace=trace)

    @staticmethod
    def _explain(constraints, bundle, layout, validation, selected):
        return {
            "summary": f"Selected {layout.strategy or 'validated'} layout for {constraints.theme or 'your requested style'}.",
            "theme": constraints.theme,
            "preferences": constraints.preferences,
            "product_reasons": [
                {"category": p["category"], "name": p["name"], "reason": "Highest-ranked compatible product included in the optimized bundle."}
                for p in bundle.get("products", [])
            ],
            "tradeoffs": [
                "Accessory costs are included in the bundle total.",
                "Only layouts that pass deterministic hard geometry checks can be selected.",
            ],
            "validation_summary": validation,
            "candidate_scores": [
                {"id": item["layout"].id, "score": item["score"], "valid": item["validation"]["valid"]}
                for item in selected.get("candidates", [])
            ],
        }
