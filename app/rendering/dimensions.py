"""Deterministic SVG dimension annotations."""
from __future__ import annotations


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def horizontal_dimension(x1: float, x2: float, y: float, label: str) -> str:
    return (
        f'<g class="dimension" data-type="horizontal">'
        f'<line x1="{fmt(x1)}" y1="{fmt(y)}" x2="{fmt(x2)}" y2="{fmt(y)}" />'
        f'<line x1="{fmt(x1)}" y1="{fmt(y-10)}" x2="{fmt(x1)}" y2="{fmt(y+10)}" />'
        f'<line x1="{fmt(x2)}" y1="{fmt(y-10)}" x2="{fmt(x2)}" y2="{fmt(y+10)}" />'
        f'<text x="{fmt((x1+x2)/2)}" y="{fmt(y-14)}" text-anchor="middle">{label}</text></g>'
    )


def vertical_dimension(x: float, y1: float, y2: float, label: str) -> str:
    return (
        f'<g class="dimension" data-type="vertical">'
        f'<line x1="{fmt(x)}" y1="{fmt(y1)}" x2="{fmt(x)}" y2="{fmt(y2)}" />'
        f'<line x1="{fmt(x-10)}" y1="{fmt(y1)}" x2="{fmt(x+10)}" y2="{fmt(y1)}" />'
        f'<line x1="{fmt(x-10)}" y1="{fmt(y2)}" x2="{fmt(x+10)}" y2="{fmt(y2)}" />'
        f'<text x="{fmt(x-14)}" y="{fmt((y1+y2)/2)}" text-anchor="middle" '
        f'transform="rotate(-90 {fmt(x-14)} {fmt((y1+y2)/2)})">{label}</text></g>'
    )
