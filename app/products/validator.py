"""Deterministic validation for product catalog integrity."""

from collections import Counter
from typing import Iterable

from app.models.product import Product
from app.config.constants import PRODUCT_CATEGORIES


def validate_catalog(products: Iterable[Product]) -> list[str]:
    products = list(products)
    errors: list[str] = []
    ids = [p.id for p in products]
    for product_id, count in Counter(ids).items():
        if count > 1:
            errors.append(f"duplicate product id: {product_id}")

    valid_ids = set(ids)
    for p in products:
        if p.category not in PRODUCT_CATEGORIES:
            errors.append(f"{p.id}: invalid category {p.category}")
        if p.price < 0:
            errors.append(f"{p.id}: negative price")
        if min(p.width, p.depth, p.height) <= 0:
            errors.append(f"{p.id}: non-positive dimensions")
        for ref in p.required_accessories + p.compatibility:
            # Compatibility may intentionally be category-independent product refs.
            if ref.startswith("SYN-") and ref not in valid_ids:
                errors.append(f"{p.id}: broken product reference {ref}")
        for key, value in p.clearance_requirements.items():
            if value < 0:
                errors.append(f"{p.id}: negative clearance {key}")
        if not p.model_number:
            errors.append(f"{p.id}: missing model number")
    return errors


def assert_valid_catalog(products: Iterable[Product]) -> None:
    errors = validate_catalog(products)
    if errors:
        raise ValueError("Catalog validation failed:\n" + "\n".join(errors))
