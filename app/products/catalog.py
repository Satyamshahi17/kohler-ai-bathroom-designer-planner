"""Catalog loading utilities for synthetic and curated product modes."""

import json
from pathlib import Path

from app.models.product import Product

DATA_DIR = Path(__file__).resolve().parent / "data"


def load_products(path: str | Path | None = None) -> list[Product]:
    """Load and validate products from a JSON array."""
    source = Path(path) if path else DATA_DIR / "synthetic_products.json"
    with source.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError(f"Catalog must contain a JSON array: {source}")
    return [Product.model_validate(item) for item in payload]
