from app.llm.vision import SpatialExtractor, validate_spatial_payload


class FakeProvider:
    def __init__(self, payload):
        self.payload = payload

    def generate_json(self, **kwargs):
        return self.payload


def _base_plan():
    return {
        "room_width": {"value": 1800, "unit": "mm", "source": "explicit_annotation", "confidence": 0.95},
        "room_depth": {"value": 2200, "unit": "mm", "source": "explicit_annotation", "confidence": 0.95},
        "walls": [], "door": None, "windows": [], "ventilation": [],
        "fixed_obstacles": [], "existing_plumbing": [], "existing_electrical": [],
        "proposed_plumbing": [], "proposed_electrical": [],
    }


def test_valid_extraction_is_exact_layout_ready_when_door_swing_known():
    plan = _base_plan()
    plan["door"] = {
        "wall": "south",
        "offset": {"value": 450, "unit": "mm", "source": "explicit_annotation", "confidence": 0.9},
        "width": {"value": 750, "unit": "mm", "source": "explicit_annotation", "confidence": 0.9},
        "hinge_position": "left",
        "opening_direction": "inward",
        "swing": {"direction": "inward", "angle": {"value": 90, "unit": "degrees", "source": "explicit_annotation", "confidence": 0.9},
                  "swing_radius": {"value": 750, "unit": "mm", "source": "explicit_annotation", "confidence": 0.9}},
    }
    result = SpatialExtractor(FakeProvider(plan)).extract("ignored.png")
    assert result.exact_layout_ready is True
    assert result.spatial_plan.room_width.value == 1800


def test_missing_dimensions_are_provisional_not_fabricated():
    plan = _base_plan()
    plan["room_width"]["value"] = None
    plan["room_width"]["source"] = "unknown"
    result = validate_spatial_payload(plan)
    assert result.exact_layout_ready is False
    assert any("room dimensions" in reason for reason in result.provisional_reasons)


def test_unknown_door_swing_is_provisional():
    plan = _base_plan()
    plan["door"] = {
        "wall": "south",
        "offset": None,
        "width": {"value": 750, "unit": "mm", "source": "explicit_annotation", "confidence": 0.9},
        "hinge_position": None,
        "opening_direction": None,
        "swing": {"direction": None, "angle": None, "swing_radius": None},
    }
    result = validate_spatial_payload(plan)
    assert result.exact_layout_ready is False
    assert any("Door swing" in reason for reason in result.provisional_reasons)
