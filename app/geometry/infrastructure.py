"""Deterministic infrastructure requirement checks."""
from __future__ import annotations

import math
from app.models.layout import Layout
from app.models.product import Product


def _point_for_wall(item: dict[str, object], room_width: float, room_depth: float) -> tuple[float, float] | None:
    wall = str(item.get("wall", "")).lower()
    try:
        offset = float(item.get("offset", 0))
    except (TypeError, ValueError):
        return None
    if wall == "south": return offset, 0.0
    if wall == "north": return offset, room_depth
    if wall == "west": return 0.0, offset
    if wall == "east": return room_width, offset
    return None


def _nearest_distance(x: float, y: float, items: list[dict[str, object]], room_width: float, room_depth: float) -> float | None:
    points = [_point_for_wall(item, room_width, room_depth) for item in items]
    distances = [math.hypot(x - px, y - py) for px, py in points if px is not None and py is not None]
    return min(distances) if distances else None


def find_infrastructure_violations(layout: Layout, products: dict[str, Product], spatial_plan=None) -> list[dict[str, object]]:
    if spatial_plan is None:
        return []
    violations: list[dict[str, object]] = []
    available = {
        "plumbing": list(spatial_plan.existing_plumbing) + list(spatial_plan.proposed_plumbing),
        "electrical": list(spatial_plan.existing_electrical) + list(spatial_plan.proposed_electrical),
    }
    for placement in layout.fixtures:
        product = products.get(placement.product_id)
        if not product:
            continue
        px, py = placement.x + product.width / 2, placement.y + product.depth / 2
        for requirement in product.infrastructure_requirements:
            req = requirement.lower()
            if req in {"water_supply", "drain", "plumbing"}:
                source = available["plumbing"]
            elif req == "electrical":
                source = available["electrical"]
            else:
                continue
            if not source:
                violations.append({
                    "type": "INFRASTRUCTURE",
                    "fixture": placement.product_id,
                    "requirement": requirement,
                    "message": f"{placement.product_id} requires {requirement}, but no corresponding infrastructure point is available",
                })
    return violations
