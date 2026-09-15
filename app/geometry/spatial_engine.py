"""Small deterministic 2D geometry primitives used by the validator.

Coordinates are millimetres, origin is the south-west corner of the room.
The engine intentionally uses simple axis-aligned rectangles; rotations are
supported through a conservative axis-aligned bounding box for non-cardinal
angles.
"""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    depth: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def top(self) -> float:
        return self.y + self.depth

    @property
    def area(self) -> float:
        return max(0.0, self.width) * max(0.0, self.depth)

    def intersects(self, other: "Rect", *, touching: bool = False) -> bool:
        if touching:
            return not (self.right < other.x or other.right < self.x or self.top < other.y or other.top < self.y)
        return not (self.right <= other.x or other.right <= self.x or self.top <= other.y or other.top <= self.y)

    def contains(self, other: "Rect", tolerance: float = 1e-6) -> bool:
        return (
            other.x >= self.x - tolerance
            and other.y >= self.y - tolerance
            and other.right <= self.right + tolerance
            and other.top <= self.top + tolerance
        )

    def expanded(self, distance: float) -> "Rect":
        return Rect(self.x - distance, self.y - distance, self.width + 2 * distance, self.depth + 2 * distance)


def footprint(x: float, y: float, width: float, depth: float, rotation: float = 0.0) -> Rect:
    """Return a conservative footprint around a fixture centre/anchor.

    Layout coordinates are the lower-left anchor. Cardinal rotations swap
    dimensions; other rotations use the enclosing bounding box.
    """
    normalized = rotation % 360
    if math.isclose(normalized % 180, 90, abs_tol=1e-6):
        width, depth = depth, width
    elif not math.isclose(normalized % 90, 0, abs_tol=1e-6):
        radians = math.radians(normalized)
        width, depth = (
            abs(width * math.cos(radians)) + abs(depth * math.sin(radians)),
            abs(width * math.sin(radians)) + abs(depth * math.cos(radians)),
        )
    return Rect(x, y, width, depth)
