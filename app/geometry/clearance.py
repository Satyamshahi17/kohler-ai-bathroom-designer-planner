"""Deterministic product clearance checks."""
from __future__ import annotations

from app.models.layout import FixturePlacement, Layout
from app.models.product import Product
from .spatial_engine import Rect, footprint


def clearance_zone(placement: FixturePlacement, product: Product) -> Rect:
    rect = footprint(placement.x, placement.y, product.width, product.depth, placement.rotation)
    front = float(product.clearance_requirements.get("front", 0))
    side = float(product.clearance_requirements.get("side", 0))
    # The product data defines front/side clearance but not orientation-specific
    # wall rules. Apply a conservative expansion around the footprint.
    return rect.expanded(max(front, side))


def find_clearance_violations(layout: Layout, products: dict[str, Product]) -> list[dict[str, object]]:
    violations: list[dict[str, object]] = []
    room = Rect(0, 0, layout.room_width, layout.room_depth)
    for placement in layout.fixtures:
        product = products.get(placement.product_id)
        if not product:
            continue
        zone = clearance_zone(placement, product)
        if not room.contains(zone):
            violations.append({
                "type": "CLEARANCE",
                "fixture": placement.product_id,
                "message": f"{placement.product_id} clearance zone extends outside the room",
            })
    return violations
