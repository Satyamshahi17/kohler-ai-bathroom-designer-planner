from app.models.layout import FixturePlacement, Layout
from app.models.product import Product
from app.models.spatial_plan import Door, DoorSwing, SpatialPlan, SourcedValue
from app.rendering.svg_renderer import SVGRenderer


def product(pid="p1", category="vanity", width=600, depth=500):
    return Product(id=pid, model_number=pid, name="Test Fixture", category=category,
                   price=100, width=width, depth=depth, height=500)


def plan():
    return SpatialPlan(
        room_width=SourcedValue(value=2400, unit="mm", source="user_provided", confidence=1),
        room_depth=SourcedValue(value=1800, unit="mm", source="user_provided", confidence=1),
        door=Door(wall="south", offset=SourcedValue(value=700, unit="mm", source="explicit_annotation", confidence=1),
                  width=SourcedValue(value=800, unit="mm", source="explicit_annotation", confidence=1),
                  hinge_position="left", opening_direction="inward",
                  swing=DoorSwing(swing_radius=SourcedValue(value=800, unit="mm", source="explicit_annotation", confidence=1))),
        windows=[{"wall": "north", "offset": 500, "width": 900}],
    )


def test_svg_contains_scaled_architecture_and_fixture():
    layout = Layout(id="demo", room_width=2400, room_depth=1800,
                    fixtures=[FixturePlacement(product_id="p1", category="vanity", x=100, y=900)])
    svg = SVGRenderer().render(layout, {"p1": product()}, plan())
    assert svg.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert 'data-room-width-mm="2400"' in svg
    assert 'data-room-depth-mm="1800"' in svg
    assert 'class="fixture"' in svg
    assert 'class="window"' in svg
    assert 'class="door-swing"' in svg
    assert '2400 mm' in svg
    assert '1800 mm' in svg


def test_svg_is_deterministic():
    layout = Layout(id="demo", room_width=2400, room_depth=1800,
                    fixtures=[FixturePlacement(product_id="p1", category="vanity", x=100, y=900)])
    products = {"p1": product()}
    renderer = SVGRenderer()
    assert renderer.render(layout, products, plan()) == renderer.render(layout, products, plan())
