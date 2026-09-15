"""Deterministic SVG legend."""
from __future__ import annotations


def render_legend(x: float, y: float) -> str:
    items = [("fixture", "Fixture"), ("window", "Window"), ("door-swing", "Door swing")]
    out = [f'<g class="legend"><text x="{x}" y="{y}" class="legend-title">Legend</text>']
    for i, (kind, label) in enumerate(items, 1):
        yy = y + i * 34
        if kind == "fixture":
            shape = f'<rect class="legend-fixture" x="{x}" y="{yy-18}" width="24" height="24" />'
        elif kind == "window":
            shape = f'<rect class="legend-window" x="{x}" y="{yy-18}" width="24" height="24" />'
        else:
            shape = f'<path class="legend-swing" d="M {x} {yy} A 24 24 0 0 1 {x+24} {yy-24}" />'
        out.append(shape + f'<text x="{x+36}" y="{yy}" dominant-baseline="middle">{label}</text>')
    out.append('</g>')
    return ''.join(out)
