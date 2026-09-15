"""Accessory resolution and cost handling for optimized bundles."""
from __future__ import annotations

from app.models.product import Product


def accessory_catalog(products: list[Product]) -> dict[str, Product]:
    return {p.id: p for p in products if p.category == "accessory"}


def required_accessories(selected_products: list[Product], catalog: dict[str, Product]) -> list[Product]:
    ids = set()
    for product in selected_products:
        ids.update(product.required_accessories)
    missing = sorted(ids - set(catalog))
    if missing:
        raise ValueError(f"Missing required accessories in catalog: {missing}")
    return [catalog[aid] for aid in sorted(ids)]
