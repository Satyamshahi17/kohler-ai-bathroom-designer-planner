"""Deterministic, scaled SVG renderer for validated bathroom layouts."""
from __future__ import annotations

from xml.sax.saxutils import escape

from app.geometry.spatial_engine import footprint
from app.models.layout import Layout
from app.models.product import Product
from app.models.spatial_plan import SpatialPlan
from .dimensions import fmt, horizontal_dimension, vertical_dimension
from .legend import render_legend
from .symbols import door_symbol, fixture_symbol, window_symbol


class SVGRenderer:
    """Render the same layout into byte-for-byte stable SVG markup."""

    def __init__(self, pixels_per_mm: float = 0.35, padding: float = 180.0):
        if pixels_per_mm <= 0:
            raise ValueError("pixels_per_mm must be positive")
        self.scale = float(pixels_per_mm)
        self.padding = float(padding)

    def render(self, layout: Layout, products: dict[str, Product], spatial_plan: SpatialPlan | None = None) -> str:
        width = float(layout.room_width)
        depth = float(layout.room_depth)
        canvas_w = width * self.scale + self.padding * 2
        canvas_h = depth * self.scale + self.padding * 2

        def sx(v: float) -> float: return self.padding + v * self.scale
        def sy(v: float) -> float: return self.padding + (depth - v) * self.scale

        parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fmt(canvas_w)} {fmt(canvas_h)}" '
            f'width="{fmt(canvas_w)}" height="{fmt(canvas_h)}" data-room-width-mm="{fmt(width)}" data-room-depth-mm="{fmt(depth)}">',
            '<title>Kohler AI Bathroom Designer - Bathroom Plan</title>',
            '<desc>Deterministic scaled 2D bathroom layout. POC only; not professional architectural or code compliance documentation.</desc>',
            '<style>.room{fill:none;stroke-width:18}.fixture{fill:#dfe7ed;stroke:#334155;stroke-width:4}.fixture text{font:18px sans-serif;fill:#0f172a}.window{fill:#bfdbfe;stroke:#1d4ed8;stroke-width:4}.door{stroke:#7c2d12;stroke-width:10}.door-swing{fill:none;stroke:#a16207;stroke-width:4;stroke-dasharray:12 8}.dimension{fill:none;stroke:#64748b;stroke-width:2}.dimension text{font:18px sans-serif;fill:#334155}.legend-title{font:bold 20px sans-serif}.legend text{font:16px sans-serif}.legend-fixture{fill:#dfe7ed;stroke:#334155;stroke-width:2}.legend-window{fill:#bfdbfe;stroke:#1d4ed8;stroke-width:2}.legend-swing{fill:none;stroke:#a16207;stroke-width:3}</style>',
            f'<rect class="room" x="{fmt(sx(0))}" y="{fmt(sy(depth))}" width="{fmt(width*self.scale)}" height="{fmt(depth*self.scale)}" />',
        ]

        # Draw architecture first, then fixtures and annotations.
        if spatial_plan:
            if spatial_plan.windows:
                for window in sorted(spatial_plan.windows, key=lambda w: (str(w.get("wall", "")), float(w.get("offset", 0) or 0))):
                    symbol = window_symbol(window, width, depth)
                    if symbol:
                        parts.append(self._transform(symbol, depth, self.scale, self.padding))
            if spatial_plan.door:
                parts.append(self._transform(door_symbol(spatial_plan.door, width, depth), depth, self.scale, self.padding))

        for placement in sorted(layout.fixtures, key=lambda p: (p.category, p.product_id, p.x, p.y)):
            product = products.get(placement.product_id)
            if product:
                parts.append(self._transform(fixture_symbol(placement, product), depth, self.scale, self.padding))

        # Dimensions are deliberately outside the room to remain readable.
        parts.append(horizontal_dimension(sx(0), sx(width), self.padding - 55, f"{fmt(width)} mm"))
        parts.append(vertical_dimension(self.padding - 55, sy(0), sy(depth), f"{fmt(depth)} mm"))
        parts.append(render_legend(self.padding, canvas_h - 120))
        parts.append('</svg>')
        return ''.join(parts)

    @staticmethod
    def _transform(markup: str, depth: float, scale: float, padding: float) -> str:
        """Convert model-space y-up SVG snippets into canvas-space y-down coordinates."""
        # Symbols are built in model coordinates. A single group transform keeps
        # the symbol definitions deterministic while flipping the y axis.
        return f'<g transform="translate({fmt(padding)} {fmt(padding + depth*scale)}) scale({fmt(scale)} {-scale:.2f})">{markup}</g>'
