from app.products.catalog import load_products
from app.products.validator import validate_catalog


def test_synthetic_catalog_has_expected_scale_and_categories():
    products = load_products()
    assert len(products) >= 100
    counts = {category: sum(p.category == category for p in products) for category in ("vanity", "faucet", "toilet", "shower", "accessory")}
    assert counts["vanity"] == 25
    assert counts["faucet"] == 25
    assert counts["toilet"] == 25
    assert counts["shower"] == 25
    assert counts["accessory"] == 20


def test_synthetic_catalog_is_valid():
    products = load_products()
    assert validate_catalog(products) == []


def test_adversarial_records_are_present():
    products = load_products()
    assert any(p.width >= 2000 and p.category == "vanity" for p in products)
    assert any("electrical" in p.infrastructure_requirements for p in products)
    assert any(p.required_accessories for p in products)
    assert any(p.price >= 4500 for p in products)
