import pytest
pytest.importorskip("pulp")

from app.models.product import Product
from app.recommendation.hybrid_ranker import RankedProduct
from app.optimization.optimizer import BundleOptimizer


def p(pid, category, price, score, accessories=None):
    product = Product(id=pid, model_number=pid, name=pid, category=category,
                      price=price, width=500, depth=500, height=500,
                      required_accessories=accessories or [])
    return product


def r(product, score):
    return RankedProduct(product, score, 1.0, 0.0, score, "test")


def test_optimizer_counts_required_accessories_and_selects_top_bundle():
    catalog = [
        p("V1", "vanity", 900, .9, ["A1"]), p("V2", "vanity", 500, .6, ["A1"]),
        p("F1", "faucet", 200, .9), p("F2", "faucet", 150, .5),
        Product(id="A1", model_number="A1", name="Accessory", category="accessory", price=100, width=10, depth=10, height=10),
    ]
    ranked = {"vanity": [r(catalog[0], .9), r(catalog[1], .6)], "faucet": [r(catalog[2], .9), r(catalog[3], .5)]}
    result = BundleOptimizer(catalog).optimize(ranked, budget=1300, top_k=2)
    assert len(result) == 2
    assert result[0].total_cost <= 1300
    assert result[0].total_accessory_cost == 100
    assert "A1" in [a.id for a in result[0].accessories]


def test_incompatibility_is_hard_constraint():
    catalog = [
        p("V1", "vanity", 500, .99), p("F1", "faucet", 100, .99),
        p("F2", "faucet", 100, .50),
    ]
    ranked = {"vanity": [r(catalog[0], .99)], "faucet": [r(catalog[1], .99), r(catalog[2], .50)]}
    result = BundleOptimizer(catalog).optimize(ranked, budget=700, incompatible_pairs=[("V1", "F1")])
    assert result[0].product_ids == ("V1", "F2")


def test_budget_fallback_reports_shortfall():
    catalog = [p("V1", "vanity", 900, .9, ["A1"]), p("F1", "faucet", 200, .9),
               Product(id="A1", model_number="A1", name="Accessory", category="accessory", price=100, width=10, depth=10, height=10)]
    ranked = {"vanity": [r(catalog[0], .9)], "faucet": [r(catalog[1], .9)]}
    result = BundleOptimizer(catalog).optimize(ranked, budget=1000)
    assert result[0].total_cost == 1200
    assert result[0].budget_feasible is False
    assert result[0].budget_shortfall == 200
