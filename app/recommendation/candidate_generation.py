"""Generate recommendation candidates using semantic search plus KG rules."""
from __future__ import annotations

from typing import Protocol

from app.models.product import Product
from app.models.user_constraints import UserConstraints
from app.products.embeddings import ProductEmbeddingIndex


class KGRules(Protocol):
    def get_theme_filtered_products(self, theme: str) -> list[dict]: ...
    def is_compatible(self, product_a: str, product_b: str) -> bool: ...


def _row_product_id(row: dict) -> str | None:
    value = row.get("id")
    if value:
        return value
    node = row.get("p")
    if isinstance(node, dict):
        return node.get("id")
    try:
        return node.get("id") if node is not None else None
    except AttributeError:
        return None


def generate_candidates(
    constraints: UserConstraints,
    products: list[Product],
    embeddings: ProductEmbeddingIndex,
    kg: KGRules | None = None,
    *,
    per_category: int = 10,
) -> dict[str, list[tuple[Product, float, bool]]]:
    """Return semantic candidates with KG theme evidence.

    KG theme filtering is used when available. It is deliberately not a hard
    elimination for categories with no theme matches; semantic retrieval is the
    documented fallback in the specification.
    """
    query = " ".join([constraints.theme, *constraints.preferences]).strip()
    result: dict[str, list[tuple[Product, float, bool]]] = {}

    for category in constraints.required_categories:
        category_products = [p for p in products if p.category == category]
        if not category_products:
            result[category] = []
            continue
        theme_ids: set[str] = set()
        if kg and constraints.theme:
            try:
                theme_ids = {
                    pid for pid in (_row_product_id(row) for row in kg.get_theme_filtered_products(constraints.theme)) if pid
                }
            except Exception:
                theme_ids = set()

        semantic = embeddings.search(query or category, category=category, top_k=max(per_category * 2, per_category))
        # Keep KG theme matches visible even if semantic rank is lower.
        by_id = {p.id: (p, score) for p, score in semantic}
        for p in category_products:
            if p.id in theme_ids and p.id not in by_id:
                by_id[p.id] = (p, 0.0)
        ranked = sorted(by_id.values(), key=lambda pair: (-pair[1], pair[0].id))[:per_category]
        result[category] = [(p, score, p.id in theme_ids) for p, score in ranked]
    return result
