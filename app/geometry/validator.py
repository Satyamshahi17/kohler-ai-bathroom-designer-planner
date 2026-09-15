"""Single deterministic authority for layout feasibility."""
from __future__ import annotations

from app.models.layout import Layout
from app.models.product import Product
from app.models.spatial_plan import SpatialPlan
from .spatial_engine import Rect
from .collision import fixture_rect, find_collisions
from .clearance import find_clearance_violations
from .door import find_door_violations
from .circulation import find_circulation_violations
from .infrastructure import find_infrastructure_violations


def _wall_segment_rect(item: dict[str, object], room_width: float, room_depth: float) -> Rect | None:
    """Convert a fixed wall feature into a thin deterministic obstacle."""
    wall = str(item.get("wall", "")).lower()
    try:
        offset = float(item.get("offset", 0))
        width = float(item.get("width", 0))
    except (TypeError, ValueError):
        return None
    if width <= 0:
        return None
    thickness = 1.0
    if wall == "south": return Rect(offset, 0, width, thickness)
    if wall == "north": return Rect(offset, room_depth - thickness, width, thickness)
    if wall == "west": return Rect(0, offset, thickness, width)
    if wall == "east": return Rect(room_width - thickness, offset, thickness, width)
    return None


def _fixed_obstacle_rect(item: dict[str, object]) -> Rect | None:
    try:
        return Rect(float(item["x"]), float(item["y"]), float(item["width"]), float(item["depth"]))
    except (KeyError, TypeError, ValueError):
        return None


def _fixed_feature_violations(layout: Layout, products: dict[str, Product], spatial_plan: SpatialPlan) -> list[dict[str, object]]:
    violations: list[dict[str, object]] = []
    room = Rect(0, 0, layout.room_width, layout.room_depth)
    obstacles: list[tuple[str, Rect]] = []

    for index, item in enumerate(spatial_plan.fixed_obstacles):
        rect = _fixed_obstacle_rect(item)
        if rect:
            obstacles.append((f"fixed_obstacle_{index + 1}", rect))

    for index, item in enumerate(spatial_plan.windows):
        rect = _wall_segment_rect(item, layout.room_width, layout.room_depth)
        if rect:
            # Windows are treated as protected wall segments for this POC.
            obstacles.append((f"window_{index + 1}", rect))

    for placement in layout.fixtures:
        product = products.get(placement.product_id)
        if not product:
            continue
        rect = fixture_rect(placement, product)
        for obstacle_id, obstacle in obstacles:
            if rect.intersects(obstacle, touching=True):
                kind = "WINDOW_OBSTRUCTION" if obstacle_id.startswith("window_") else "FIXED_OBSTACLE"
                violations.append({
                    "type": kind,
                    "fixture": placement.product_id,
                    "obstacle": obstacle_id,
                    "message": f"{placement.product_id} intersects {obstacle_id}",
                })
    return violations


class GeometryValidator:
    """Validate layouts using deterministic geometric/domain rules only."""

    def validate(self, layout: Layout, products: dict[str, Product], spatial_plan: SpatialPlan | None = None) -> dict[str, object]:
        violations: list[dict[str, object]] = []
        room = Rect(0, 0, layout.room_width, layout.room_depth)
        for placement in layout.fixtures:
            product = products.get(placement.product_id)
            if product is None:
                violations.append({
                    "type": "UNKNOWN_PRODUCT",
                    "fixture": placement.product_id,
                    "message": "Product is not present in the supplied catalog",
                })
                continue
            rect = fixture_rect(placement, product)
            if not room.contains(rect):
                violations.append({
                    "type": "ROOM_BOUNDS",
                    "fixture": placement.product_id,
                    "message": f"{placement.product_id} extends outside room bounds",
                })

        violations.extend(find_collisions(layout, products))
        violations.extend(find_clearance_violations(layout, products))
        violations.extend(find_door_violations(layout, spatial_plan.door if spatial_plan else None, products))
        violations.extend(find_circulation_violations(layout, products))
        violations.extend(find_infrastructure_violations(layout, products, spatial_plan))
        if spatial_plan:
            violations.extend(_fixed_feature_violations(layout, products, spatial_plan))

        hard_types = {
            "ROOM_BOUNDS", "COLLISION", "DOOR_SWING", "CLEARANCE",
            "INFRASTRUCTURE", "UNKNOWN_PRODUCT", "WINDOW_OBSTRUCTION",
            "FIXED_OBSTACLE",
        }
        hard_violations = [v for v in violations if v["type"] in hard_types]
        return {
            "valid": not hard_violations,
            "violations": violations,
            "hard_violation_count": len(hard_violations),
            "checked_rules": [
                "room_bounds", "collision", "clearance", "door_swing",
                "circulation", "windows", "fixed_obstacles", "infrastructure",
            ],
        }
