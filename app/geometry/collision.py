"""Deterministic fixture collision checks."""
from __future__ import annotations

from app.models.layout import FixturePlacement, Layout
from app.models.product import Product
from .spatial_engine import footprint, Rect


def fixture_rect(placement: FixturePlacement, product: Product) -> Rect:
    return footprint(placement.x, placement.y, product.width, product.depth, placement.rotation)


def find_collisions(layout: Layout, products: dict[str, Product]) -> list[dict[str, object]]:
    violations: list[dict[str, object]] = []
    placed = [(p, fixture_rect(p, products[p.product_id])) for p in layout.fixtures if p.product_id in products]
    for i, (left, left_rect) in enumerate(placed):
        for right, right_rect in placed[i + 1 :]:
            if left_rect.intersects(right_rect):
                violations.append({
                    "type": "COLLISION",
                    "fixtures": [left.product_id, right.product_id],
                    "message": f"{left.product_id} overlaps {right.product_id}",
                })
    return violations
