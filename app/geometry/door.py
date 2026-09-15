"""Door and swing-region geometry."""
from __future__ import annotations

import math
from app.models.layout import Layout
from app.models.spatial_plan import Door
from app.models.product import Product
from .collision import fixture_rect
from .spatial_engine import Rect


def _swing_rect(layout: Layout, door: Door) -> Rect | None:
    if not door.wall or not door.width or door.width.value is None:
        return None
    if door.opening_direction != "inward":
        return None
    radius_value = door.swing.swing_radius.value if door.swing and door.swing.swing_radius else None
    angle_value = door.swing.angle.value if door.swing and door.swing.angle else None
    if radius_value is None:
        return None
    radius = float(radius_value)
    angle = float(angle_value) if angle_value is not None else 90.0
    # For an inward quarter/partial swing, a conservative bounding sector box
    # is used. It intentionally over-approximates the true arc.
    wall = door.wall.lower()
    offset = float(door.offset.value) if door.offset and door.offset.value is not None else 0.0
    width = float(door.width.value)
    if wall == "south":
        hinge_x = offset if door.hinge_position != "right" else offset + width
        hinge_y = 0.0
    elif wall == "north":
        hinge_x = offset if door.hinge_position != "right" else offset + width
        hinge_y = layout.room_depth
    elif wall == "west":
        hinge_x = 0.0
        hinge_y = offset if door.hinge_position != "right" else offset + width
    elif wall == "east":
        hinge_x = layout.room_width
        hinge_y = offset if door.hinge_position != "right" else offset + width
    else:
        return None

    # A 90° inward swing is represented by a radius-sized square clipped to
    # room bounds. For other angles this remains a safe conservative envelope.
    raw = Rect(hinge_x - radius, hinge_y - radius, 2 * radius, 2 * radius)
    room = Rect(0, 0, layout.room_width, layout.room_depth)
    x1, y1 = max(0, raw.x), max(0, raw.y)
    x2, y2 = min(layout.room_width, raw.right), min(layout.room_depth, raw.top)
    if x2 <= x1 or y2 <= y1:
        return None
    return Rect(x1, y1, x2 - x1, y2 - y1)


def find_door_violations(layout: Layout, door: Door | None, products: dict[str, Product]) -> list[dict[str, object]]:
    if door is None or door.opening_direction != "inward":
        return []
    swing = _swing_rect(layout, door)
    if swing is None:
        return [{"type": "DOOR_SWING_UNKNOWN", "message": "Door swing cannot be deterministically validated from the available measurements"}]
    violations: list[dict[str, object]] = []
    for placement in layout.fixtures:
        product = products.get(placement.product_id)
        if product and fixture_rect(placement, product).intersects(swing):
            violations.append({
                "type": "DOOR_SWING",
                "fixture": placement.product_id,
                "message": f"{placement.product_id} intersects the door swing zone",
            })
    return violations
