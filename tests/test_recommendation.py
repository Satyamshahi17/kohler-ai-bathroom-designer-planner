from app.models.product import Product
from app.models.user_constraints import UserConstraints
from app.products.embeddings import ProductEmbeddingIndex, lexical_similarity, product_text
from app.recommendation.hybrid_ranker import HybridRanker


class FakeKG:
    def __init__(self):
        self.theme = {"P1"}
        self.incompatible = {frozenset({"P1", "P2"})}

    def get_theme_filtered_products(self, theme):
        return [{"p": {"id": x}} for x in self.theme] if theme.lower() == "japanese zen" else []

    def is_compatible(self, a, b):
        return frozenset({a, b}) not in self.incompatible


def product(pid, category, name, tags):
    return Product(
        id=pid, model_number=pid, name=name, category=category, price=100,
        width=500, depth=500, height=500, style_tags=tags
    )


def test_lexical_similarity_prefers_matching_style():
    assert lexical_similarity("warm japanese zen", "warm japanese zen minimal") > lexical_similarity("warm japanese zen", "industrial chrome")


def test_kg_theme_match_is_reflected_in_ranker():
    products = [product("P1", "vanity", "Zen Vanity", ["japanese-zen", "warm"]), product("P2", "vanity", "Modern Vanity", ["modern"])]
    index = ProductEmbeddingIndex(products, use_model=False)
    constraints = UserConstraints(budget=1000, theme="Japanese Zen", required_categories=["vanity"], preferences=["warm"])
    ranked = HybridRanker(products, index, FakeKG()).rank(constraints)
    assert ranked["vanity"][0].product.id == "P1"
    assert ranked["vanity"][0].kg_score == 1.0


def test_explicit_incompatibility_cannot_be_overridden_by_semantic_score():
    products = [product("P1", "vanity", "Zen Vanity", ["japanese-zen"]), product("P2", "faucet", "Zen Faucet", ["japanese-zen"])]
    index = ProductEmbeddingIndex(products, use_model=False)
    constraints = UserConstraints(budget=1000, theme="Japanese Zen", required_categories=["vanity", "faucet"])
    ranker = HybridRanker(products, index, FakeKG())
    ranked = ranker.rank(constraints)
    filtered = ranker.filter_compatible(ranked)
    # P1 is accepted first; incompatible P2 is removed.
    assert filtered["vanity"]
    assert filtered["faucet"] == []
