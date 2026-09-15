from app.layout.candidate_generator import LayoutCandidateGenerator
from app.layout.refinement import LayoutRefiner
from app.layout.selector import LayoutSelector
from app.models.product import Product
from app.models.spatial_plan import SpatialPlan, SourcedValue


def product(pid, category, w=500, d=500):
    return Product(id=pid, model_number=pid, name=pid, category=category, price=100,
                   width=w, depth=d, height=500, clearance_requirements={"front": 0, "side": 0})


def plan():
    return SpatialPlan(room_width=SourcedValue(value=3000, unit="mm", source="user_provided", confidence=1),
                       room_depth=SourcedValue(value=2500, unit="mm", source="user_provided", confidence=1))


def test_generates_three_to_five_candidates():
    products = {"v": product("v", "vanity"), "t": product("t", "toilet"), "s": product("s", "shower")}
    candidates = LayoutCandidateGenerator().generate(plan(), products, {"product_ids": ["v", "t", "s"]})
    assert 3 <= len(candidates) <= 5


def test_selector_accepts_valid_candidate():
    products = {"v": product("v", "vanity"), "t": product("t", "toilet"), "s": product("s", "shower")}
    candidates = LayoutCandidateGenerator().generate(plan(), products, {"product_ids": ["v", "t", "s"]})
    result = LayoutSelector().select(candidates, products, plan(), "Japanese Zen", ["minimal"])
    assert result["total_count"] == len(candidates)
    assert result["best"] is not None


def test_refiner_reduces_simple_bounds_violation():
    products = {"v": product("v", "vanity", 1000, 500)}
    from app.models.layout import Layout, FixturePlacement
    bad = Layout(id="bad", room_width=2000, room_depth=2000,
                 fixtures=[FixturePlacement(product_id="v", category="vanity", x=1900, y=1900)])
    refined, validation, iterations = LayoutRefiner(max_iterations=3).refine(bad, products, plan())
    assert iterations >= 1
    assert refined.fixtures[0].x >= 0
    assert "violations" in validation
