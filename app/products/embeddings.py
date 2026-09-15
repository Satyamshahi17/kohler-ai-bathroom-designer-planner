"""Local semantic product embeddings using sentence-transformers.

The transformer model is loaded lazily so the rest of the application and unit
suite can run without downloading a model. A deterministic lexical fallback is
provided for offline development; production semantic mode uses the requested
all-MiniLM-L6-v2 model.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from typing import Sequence

from app.models.product import Product

DEFAULT_MODEL = "all-MiniLM-L6-v2"


def product_text(product: Product) -> str:
    fields = [
        product.name,
        product.description,
        " ".join(product.style_tags),
        product.finish or "",
        product.category,
        product.installation_type or "",
        product.faucet_configuration or "",
    ]
    return " ".join(fields)


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower().replace("-", " "))


def lexical_similarity(query: str, text: str) -> float:
    """Deterministic offline similarity in [0, 1]."""
    q = Counter(_tokens(query))
    d = Counter(_tokens(text))
    if not q or not d:
        return 0.0
    intersection = sum(min(q[token], d[token]) for token in q)
    q_norm = math.sqrt(sum(v * v for v in q.values()))
    d_norm = math.sqrt(sum(v * v for v in d.values()))
    dot = sum(q[token] * d.get(token, 0) for token in q)
    cosine = dot / (q_norm * d_norm) if q_norm and d_norm else 0.0
    coverage = intersection / sum(q.values())
    return min(1.0, 0.75 * cosine + 0.25 * coverage)


class ProductEmbeddingIndex:
    """Semantic index backed by a local SentenceTransformer model."""

    def __init__(self, products: Sequence[Product], model_name: str = DEFAULT_MODEL, *, use_model: bool = True):
        self.products = list(products)
        self.model_name = model_name
        self._model = None
        self._embeddings = None
        if use_model:
            self._load_model()

    def _load_model(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            return
        try:
            self._model = SentenceTransformer(self.model_name)
            self._embeddings = self._model.encode(
                [product_text(p) for p in self.products], normalize_embeddings=True
            )
        except Exception:
            # Offline environments may have the package but not the model.
            self._model = None
            self._embeddings = None

    @property
    def semantic_enabled(self) -> bool:
        return self._model is not None and self._embeddings is not None

    def search(self, query: str, *, category: str | None = None, top_k: int = 20) -> list[tuple[Product, float]]:
        candidates = [
            (i, p) for i, p in enumerate(self.products) if category is None or p.category == category
        ]
        if not candidates:
            return []
        if self.semantic_enabled:
            query_embedding = self._model.encode([query], normalize_embeddings=True)[0]
            ranked = [(p, float(self._embeddings[i] @ query_embedding)) for i, p in candidates]
        else:
            ranked = [(p, lexical_similarity(query, product_text(p))) for _, p in candidates]
        return sorted(ranked, key=lambda item: (-item[1], item[0].id))[:top_k]
