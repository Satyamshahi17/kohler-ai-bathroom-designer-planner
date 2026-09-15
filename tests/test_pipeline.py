from app.layout.candidate_generator import LayoutCandidateGenerator
from app.layout.selector import LayoutSelector
from app.models.product import Product
from app.models.spatial_plan import SpatialPlan, SourcedValue
from app.models.user_constraints import UserConstraints
from app.optimization.optimizer import Bundle
from app.pipeline.orchestrator import DesignPipeline


class FakeParser:
    def parse(self, text):
        return UserConstraints(budget=5000, theme="Japanese Zen",
                               required_categories=["vanity", "toilet", "shower"],
                               preferences=["minimal"])


class FakeRanker:
    pass


class FakeOptimizer:
    def __init__(self, products):
        self.products = products

    def optimize(self, ranked, budget, *, top_k=3, incompatible_pairs=()):
        selected = [ranked[c][0].product for c in ranked]
        return [Bundle(products=tuple(selected), accessories=tuple(),
                       total_product_cost=sum(p.price for p in selected), total_accessory_cost=0,
                       total_cost=sum(p.price for p in selected), score=3.0,
                       budget_feasible=sum(p.price for p in selected) <= budget,
                       constraint_satisfaction={"one_per_category": True, "budget": True})]


class FakeEmbeddings:
    def search(self, query, *, category=None, top_k=20):
        return [(p, 0.8) for p in PRODUCTS if p.category == category][:top_k]


PRODUCTS = [
    Product(id="v", model_number="v", name="Zen Vanity", category="vanity", price=1000, width=700, depth=450, height=600),
    Product(id="t", model_number="t", name="Zen Toilet", category="toilet", price=900, width=650, depth=700, height=500),
    Product(id="s", model_number="s", name="Zen Shower", category="shower", price=1100, width=800, depth=800, height=2200),
]


def spatial_plan():
    return SpatialPlan(room_width=SourcedValue(value=3000, unit="mm", source="user_provided", confidence=1),
                       room_depth=SourcedValue(value=2500, unit="mm", source="user_provided", confidence=1))


def test_pipeline_runs_through_svg_with_injected_services():
    pipeline = DesignPipeline(
        catalog=PRODUCTS,
        embeddings=FakeEmbeddings(),
        requirements_parser=FakeParser(),
        optimizer=FakeOptimizer(PRODUCTS),
        layout_generator=LayoutCandidateGenerator(candidate_count=4),
        layout_selector=LayoutSelector(),
    )
    result = pipeline.run(requirements="anything", spatial_plan=spatial_plan())
    assert result.status == "success"
    assert result.svg.startswith("<?xml")
    assert result.layout is not None
    assert result.validation["valid"] is True
    assert result.bundle["total_cost"] == 3000
    assert result.trace[-1]["stage"] == "rendering"
