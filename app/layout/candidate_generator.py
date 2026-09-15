"""Generate deterministic baseline layout candidates for a product bundle.

The LLM layout planner can replace/augment these proposals later. Every candidate
is still validated by the deterministic geometry engine before selection.
"""
from __future__ import annotations

from app.models.layout import FixturePlacement, Layout
from app.models.product import Product
from app.models.spatial_plan import SpatialPlan


class LayoutCandidateGenerator:
    def __init__(self, candidate_count: int = 4):
        self.candidate_count = max(3, min(5, candidate_count))

    def generate(self, spatial_plan: SpatialPlan, products: dict[str, Product],
                 bundle: dict[str, object]) -> list[Layout]:
        width = float(spatial_plan.room_width.value or 0)
        depth = float(spatial_plan.room_depth.value or 0)
        if width <= 0 or depth <= 0:
            raise ValueError("Room dimensions are required to generate layout candidates")

        selected = self._selected_products(bundle, products)
        if not selected:
            raise ValueError("Bundle contains no products")

        strategies = ["wall-balanced", "plumbing-first", "perimeter-zoning", "open-circulation", "compact"][:self.candidate_count]
        return [self._build(strategy, width, depth, selected, spatial_plan, i + 1)
                for i, strategy in enumerate(strategies)]

    @staticmethod
    def _selected_products(bundle: dict[str, object], products: dict[str, Product]) -> list[Product]:
        ids = bundle.get("product_ids", [])
        if isinstance(ids, dict):
            ids = list(ids.values())
        if not ids and isinstance(bundle.get("products"), list):
            ids = [p.get("product_id", p.get("id")) for p in bundle["products"] if isinstance(p, dict)]
        return [products[str(pid)] for pid in ids if pid and str(pid) in products]

    def _build(self, strategy: str, width: float, depth: float,
               selected: list[Product], plan: SpatialPlan, index: int) -> Layout:
        # Anchors are lower-left coordinates. Fixtures are placed along walls,
        # with small deterministic offsets to create meaningfully different candidates.
        placements: list[FixturePlacement] = []
        margin = 20.0
        groups = {p.category: p for p in selected}
        vanity, toilet, shower = groups.get("vanity"), groups.get("toilet"), groups.get("shower")

        if strategy == "wall-balanced":
            anchors = [(margin, depth - (vanity.depth if vanity else 0) - margin),
                       (width - (toilet.width if toilet else 0) - margin, margin),
                       (margin, margin)]
        elif strategy == "plumbing-first":
            anchors = [(margin, margin), (margin, depth * 0.42),
                       (width - (shower.width if shower else 0) - margin, margin)]
        elif strategy == "perimeter-zoning":
            anchors = [(width * .45, depth - (vanity.depth if vanity else 0) - margin),
                       (margin, depth * .35), (width - (shower.width if shower else 0) - margin, margin)]
        elif strategy == "open-circulation":
            anchors = [(width * .05, depth * .68), (width * .55, depth * .45), (width * .55, margin)]
        else:
            anchors = [(margin, margin), (width * .40, margin), (width * .40, depth * .50)]

        for p, (x, y) in zip([vanity, toilet, shower], anchors):
            if p:
                placements.append(FixturePlacement(product_id=p.id, category=p.category, x=max(0, x), y=max(0, y)))

        # Place remaining categories/accessories as non-spatial products only when they
        # have dimensions; accessories are not part of the fixture layout by default.
        for p in selected:
            if p.category in {"vanity", "toilet", "shower"}:
                continue
            if p.category == "faucet":
                continue  # mounted to vanity; represented through the bundle, not footprint
            if p.width <= width and p.depth <= depth:
                x = max(margin, width - p.width - margin)
                y = max(margin, depth - p.depth - margin)
                placements.append(FixturePlacement(product_id=p.id, category=p.category, x=x, y=y))

        return Layout(id=f"candidate-{index}", room_width=width, room_depth=depth,
                      fixtures=placements, strategy=strategy)
