"""Hybrid KG + semantic product ranker."""
from __future__ import annotations

from dataclasses import dataclass

from app.models.product import Product
from app.models.user_constraints import UserConstraints
from app.products.embeddings import ProductEmbeddingIndex
from .candidate_generation import generate_candidates
from .scoring import score_product


@dataclass(frozen=True)
class RankedProduct:
    product: Product
    semantic_score: float
    kg_score: float
    preference_score: float
    hybrid_score: float
    reason: str

    def as_dict(self) -> dict:
        return {
            "product": self.product.model_dump(),
            "scores": {
                "semantic": self.semantic_score,
                "kg": self.kg_score,
                "preference": self.preference_score,
                "hybrid": self.hybrid_score,
            },
            "reason": self.reason,
        }


class HybridRanker:
    def __init__(self, products: list[Product], embeddings: ProductEmbeddingIndex, kg=None):
        self.products = products
        self.embeddings = embeddings
        self.kg = kg

    def rank(self, constraints: UserConstraints, *, per_category: int = 10) -> dict[str, list[RankedProduct]]:
        candidates = generate_candidates(
            constraints, self.products, self.embeddings, self.kg, per_category=per_category
        )
        ranked: dict[str, list[RankedProduct]] = {}
        for category, items in candidates.items():
            output = []
            for product, semantic, theme_match in items:
                scores = score_product(
                    product, semantic, theme_match=theme_match, preferences=constraints.preferences
                )
                reason_parts = []
                if theme_match:
                    reason_parts.append(f"explicit KG theme match for {constraints.theme}")
                elif constraints.theme:
                    reason_parts.append("semantic fallback used because no explicit KG theme match was available")
                if scores["preference_score"] > 0:
                    reason_parts.append("matches user preferences")
                reason_parts.append(f"semantic similarity {scores['semantic_score']:.2f}")
                output.append(
                    RankedProduct(
                        product=product,
                        semantic_score=scores["semantic_score"],
                        kg_score=scores["kg_score"],
                        preference_score=scores["preference_score"],
                        hybrid_score=scores["hybrid_score"],
                        reason="; ".join(reason_parts),
                    )
                )
            ranked[category] = sorted(output, key=lambda x: (-x.hybrid_score, x.product.id))
        return ranked

    def filter_compatible(self, ranked: dict[str, list[RankedProduct]]) -> dict[str, list[RankedProduct]]:
        """Remove candidates with explicit KG incompatibilities only.

        Semantic similarity can never override an explicit incompatibility.
        """
        if not self.kg:
            return ranked
        categories = list(ranked)
        accepted: dict[str, list[RankedProduct]] = {c: [] for c in categories}
        for category in categories:
            for candidate in ranked[category]:
                incompatible = False
                for other_category in categories:
                    for other in accepted[other_category]:
                        try:
                            if not self.kg.is_compatible(candidate.product.id, other.product.id):
                                incompatible = True
                                break
                        except Exception:
                            # An unavailable KG must not be treated as an incompatibility.
                            continue
                    if incompatible:
                        break
                if not incompatible:
                    accepted[category].append(candidate)
        return accepted
