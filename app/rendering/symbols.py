"""Deterministic SVG symbols for architectural elements and fixtures."""
from __future__ import annotations
import math
from xml.sax.saxutils import escape

from app.geometry.spatial_engine import footprint
from app.models.layout import FixturePlacement
from app.models.product import Product


def fmt(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


def fixture_symbol(placement: FixturePlacement, product: Product) -> str:
    rect = footprint(placement.x, placement.y, product.width, product.depth, placement.rotation)
    label = escape(product.name)
    return (
        f'<g class="fixture" data-product-id="{escape(product.id)}" data-category="{escape(product.category)}">'
        f'<rect x="{fmt(rect.x)}" y="{fmt(rect.y)}" width="{fmt(rect.width)}" height="{fmt(rect.depth)}" rx="8" />'
        f'<text x="0" y="0" transform="translate({fmt(rect.x + rect.width/2)} {fmt(rect.y + rect.depth/2)}) scale(1,-1)" '
        f'text-anchor="middle" dominant-baseline="middle">{label}</text></g>'
    )


def window_symbol(window: dict[str, object], room_width: float, room_depth: float) -> str:
    wall = str(window.get("wall", "")).lower()
    offset = float(window.get("offset", 0) or 0)
    width = float(window.get("width", 0) or 0)
    if width <= 0:
        return ""
    if wall == "south": x, y, w, h = offset, 0, width, 14
    elif wall == "north": x, y, w, h = offset, room_depth-14, width, 14
    elif wall == "west": x, y, w, h = 0, offset, 14, width
    elif wall == "east": x, y, w, h = room_width-14, offset, 14, width
    else: return ""
    return f'<rect class="window" x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" />'


def door_symbol(door, room_width: float, room_depth: float) -> str:
    if not door or not door.wall or not door.width or door.width.value is None:
        return ""
    wall = door.wall.lower()
    offset = float(door.offset.value) if door.offset and door.offset.value is not None else 0
    width = float(door.width.value)
    hinge_right = door.hinge_position == "right"
    radius = None
    if door.swing and door.swing.swing_radius and door.swing.swing_radius.value is not None:
        radius = float(door.swing.swing_radius.value)
    parts = []
    if wall == "south":
        hx = offset + (width if hinge_right else 0); hy = 0
        ex = hx + (0 if hinge_right else width); ey = hy + (radius or width)
        parts.append(f'<line class="door" x1="{fmt(hx)}" y1="{fmt(hy)}" x2="{fmt(ex)}" y2="{fmt(hy)}" />')
        if radius: parts.append(f'<path class="door-swing" d="M {fmt(ex)} {fmt(hy)} A {fmt(radius)} {fmt(radius)} 0 0 {1 if hinge_right else 0} {fmt(hx)} {fmt(ey)}" />')
    elif wall == "north":
        hx = offset + (width if hinge_right else 0); hy = room_depth
        ex = hx + (0 if hinge_right else width); ey = hy - (radius or width)
        parts.append(f'<line class="door" x1="{fmt(hx)}" y1="{fmt(hy)}" x2="{fmt(ex)}" y2="{fmt(hy)}" />')
        if radius: parts.append(f'<path class="door-swing" d="M {fmt(ex)} {fmt(hy)} A {fmt(radius)} {fmt(radius)} 0 0 {0 if hinge_right else 1} {fmt(hx)} {fmt(ey)}" />')
    elif wall == "west":
        hx = 0; hy = offset + (width if hinge_right else 0)
        ex = (radius or width); ey = hy + (0 if hinge_right else width)
        parts.append(f'<line class="door" x1="{fmt(hx)}" y1="{fmt(hy)}" x2="{fmt(hx)}" y2="{fmt(ey)}" />')
        if radius: parts.append(f'<path class="door-swing" d="M {fmt(hx)} {fmt(ey)} A {fmt(radius)} {fmt(radius)} 0 0 {0 if hinge_right else 1} {fmt(ex)} {fmt(hy)}" />')
    elif wall == "east":
        hx = room_width; hy = offset + (width if hinge_right else 0)
        ex = room_width - (radius or width); ey = hy + (0 if hinge_right else width)
        parts.append(f'<line class="door" x1="{fmt(hx)}" y1="{fmt(hy)}" x2="{fmt(hx)}" y2="{fmt(ey)}" />')
        if radius: parts.append(f'<path class="door-swing" d="M {fmt(hx)} {fmt(ey)} A {fmt(radius)} {fmt(radius)} 0 0 {1 if hinge_right else 0} {fmt(ex)} {fmt(hy)}" />')
    return '<g class="door-group">' + ''.join(parts) + '</g>'
