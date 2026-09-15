"""Deterministic circulation checks."""
from __future__ import annotations

from app.models.layout import Layout
from app.models.product import Product
from .spatial_engine import Rect
from .collision import fixture_rect

DEFAULT_CIRCULATION_WIDTH = 600.0


def find_circulation_violations(layout: Layout, products: dict[str, Product], minimum_width: float = DEFAULT_CIRCULATION_WIDTH) -> list[dict[str, object]]:
    if len(layout.fixtures) < 2:
        return []
    # Approximate the central usable corridor. This is deliberately a simple
    # POC rule, not a building-code claim.
    room = Rect(0, 0, layout.room_width, layout.room_depth)
    obstacles = [fixture_rect(p, products[p.product_id]) for p in layout.fixtures if p.product_id in products]
    # If every horizontal or vertical centreline is blocked, report reduced circulation.
    x_clear = any(all(not (r.x <= x <= r.right) for r in obstacles) for x in [room.x + room.width / 2])
    y_clear = any(all(not (r.y <= y <= r.top) for r in obstacles) for y in [room.y + room.depth / 2])
    if not x_clear and not y_clear and min(room.width, room.depth) < minimum_width:
        return [{"type": "CIRCULATION", "message": "No sufficiently wide central circulation path is available"}]
    return []
