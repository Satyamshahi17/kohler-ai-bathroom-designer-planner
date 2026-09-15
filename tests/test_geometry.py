from app.geometry.validator import GeometryValidator
from app.models.layout import FixturePlacement, Layout
from app.models.product import Product
from app.models.spatial_plan import Door, DoorSwing, SpatialPlan, SourcedValue


def product(pid="p1", width=500, depth=500, clear_front=0):
    return Product(
        id=pid, model_number=pid, name=pid, category="vanity", price=100,
        width=width, depth=depth, height=500,
        clearance_requirements={"front": clear_front, "side": 0},
    )


def plan(width=1800, depth=2200, door=None):
    return SpatialPlan(
        room_width=SourcedValue(value=width, unit="mm", source="user_provided", confidence=1),
        room_depth=SourcedValue(value=depth, unit="mm", source="user_provided", confidence=1),
        door=door,
    )


def test_room_bounds_violation():
    layout = Layout(id="x", room_width=1800, room_depth=2200, fixtures=[FixturePlacement(product_id="p1", category="vanity", x=1500, y=0)])
    result = GeometryValidator().validate(layout, {"p1": product()}, plan())
    assert not result["valid"]
    assert any(v["type"] == "ROOM_BOUNDS" for v in result["violations"])


def test_collision_is_detected():
    p = {"a": product("a"), "b": product("b")}
    layout = Layout(id="x", room_width=1800, room_depth=2200, fixtures=[
        FixturePlacement(product_id="a", category="vanity", x=100, y=100),
        FixturePlacement(product_id="b", category="toilet", x=400, y=100),
    ])
    assert any(v["type"] == "COLLISION" for v in GeometryValidator().validate(layout, p, plan())["violations"])


def test_clearance_is_checked():
    layout = Layout(id="x", room_width=1800, room_depth=2200, fixtures=[FixturePlacement(product_id="p1", category="vanity", x=100, y=100)])
    result = GeometryValidator().validate(layout, {"p1": product(clear_front=600)}, plan())
    assert any(v["type"] == "CLEARANCE" for v in result["violations"])


def test_inward_door_swing_conflict():
    door = Door(
        wall="south",
        offset=SourcedValue(value=450, unit="mm", source="explicit_annotation", confidence=1),
        width=SourcedValue(value=750, unit="mm", source="explicit_annotation", confidence=1),
        hinge_position="left", opening_direction="inward",
        swing=DoorSwing(
            angle=SourcedValue(value=90, unit="deg", source="explicit_annotation", confidence=1),
            swing_radius=SourcedValue(value=750, unit="mm", source="explicit_annotation", confidence=1),
        ),
    )
    layout = Layout(id="x", room_width=1800, room_depth=2200, fixtures=[FixturePlacement(product_id="p1", category="vanity", x=100, y=100)])
    result = GeometryValidator().validate(layout, {"p1": product()}, plan(door=door))
    assert any(v["type"] == "DOOR_SWING" for v in result["violations"])


def test_unknown_door_swing_is_not_fabricated():
    door = Door(wall="south", opening_direction="inward")
    layout = Layout(id="x", room_width=1800, room_depth=2200, fixtures=[])
    result = GeometryValidator().validate(layout, {}, plan(door=door))
    assert any(v["type"] == "DOOR_SWING_UNKNOWN" for v in result["violations"])


def test_fixed_obstacle_is_hard_constraint():
    spatial = plan()
    spatial.fixed_obstacles = [{"x": 100, "y": 100, "width": 600, "depth": 400}]
    layout = Layout(id="x", room_width=1800, room_depth=2200, fixtures=[FixturePlacement(product_id="p1", category="vanity", x=200, y=200)])
    result = GeometryValidator().validate(layout, {"p1": product()}, spatial)
    assert any(v["type"] == "FIXED_OBSTACLE" for v in result["violations"])


def test_window_obstruction_is_detected():
    spatial = plan()
    spatial.windows = [{"wall": "east", "offset": 500, "width": 900}]
    layout = Layout(id="x", room_width=1800, room_depth=2200, fixtures=[FixturePlacement(product_id="p1", category="vanity", x=1799, y=600)])
    result = GeometryValidator().validate(layout, {"p1": product()}, spatial)
    assert any(v["type"] == "WINDOW_OBSTRUCTION" for v in result["violations"])
