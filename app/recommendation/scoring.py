"""Deterministic scoring components for hybrid recommendation."""
from __future__ import annotations

from app.models.product import Product


def preference_score(product: Product, preferences: list[str]) -> float:
    if not preferences:
        return 0.0
    tags = {tag.lower().replace(" ", "-") for tag in product.style_tags}
    finish = (product.finish or "").lower()
    text = f"{product.name} {product.description} {finish}".lower()
    matches = 0
    for pref in preferences:
        p = pref.lower().strip().replace(" ", "-")
        if p in tags or p.replace("-", " ") in text or p in text:
            matches += 1
    return matches / len(preferences)


def product_score(semantic: float, kg_match: float, preference: float) -> float:
    """Blend semantic fit with explicit KG/theme and user preference evidence."""
    return 0.55 * semantic + 0.30 * kg_match + 0.15 * preference


def score_product(product: Product, semantic: float, *, theme_match: bool, preferences: list[str]) -> dict:
    pref = preference_score(product, preferences)
    kg = 1.0 if theme_match else 0.0
    return {
        "product_id": product.id,
        "semantic_score": round(max(0.0, min(1.0, semantic)), 4),
        "kg_score": kg,
        "preference_score": round(pref, 4),
        "hybrid_score": round(product_score(semantic, kg, pref), 4),
    }
