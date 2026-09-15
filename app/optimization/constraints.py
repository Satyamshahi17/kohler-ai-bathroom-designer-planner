"""Reusable deterministic bundle constraints."""
from __future__ import annotations

from collections.abc import Iterable


def normalize_pair(a: str, b: str) -> frozenset[str]:
    return frozenset((a, b))


def collect_required_accessories(products: Iterable) -> set[str]:
    accessories: set[str] = set()
    for product in products:
        accessories.update(product.required_accessories)
    return accessories


def has_incompatibility(product_ids: Iterable[str], incompatible_pairs: Iterable[tuple[str, str]]) -> bool:
    selected = set(product_ids)
    return any(a in selected and b in selected for a, b in incompatible_pairs)
