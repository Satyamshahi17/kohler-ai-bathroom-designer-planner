"""Generate deterministic synthetic bathroom plans and gold-standard extraction targets."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLANS = ROOT / "evaluation" / "bathroom_plans"
GOLD = ROOT / "evaluation" / "expected_outputs"
PLANS.mkdir(parents=True, exist_ok=True)
GOLD.mkdir(parents=True, exist_ok=True)

scenarios = [
    {
        "id": "plan_01_small_south_door",
        "description": "Small rectangular bathroom, south inward door, east window.",
        "room": {"width": 1800, "depth": 2200, "unit": "mm"},
        "door": {"wall": "south", "offset": 450, "width": 750, "hinge_position": "left", "opening_direction": "inward", "swing_angle": 90, "swing_radius": 750},
        "windows": [{"wall": "east", "offset": 500, "width": 900}],
        "ventilation": [{"wall": "north", "type": "exhaust_fan"}],
        "fixed_obstacles": [],
        "existing_plumbing": [{"wall": "west", "type": "supply", "offset": 400}, {"wall": "north", "type": "drain", "offset": 300}],
        "existing_electrical": [{"wall": "east", "offset": 1600}],
    },
    {
        "id": "plan_02_medium_north_door",
        "description": "Medium bathroom with north sliding-style entry representation and west window.",
        "room": {"width": 2400, "depth": 3000, "unit": "mm"},
        "door": {"wall": "north", "offset": 900, "width": 800, "hinge_position": "right", "opening_direction": "inward", "swing_angle": 90, "swing_radius": 800},
        "windows": [{"wall": "west", "offset": 900, "width": 1000}],
        "ventilation": [{"wall": "east", "type": "window_vent"}],
        "fixed_obstacles": [{"type": "column", "x": 1900, "y": 400, "width": 250, "depth": 250}],
        "existing_plumbing": [{"wall": "north", "type": "water_supply", "offset": 1300}, {"wall": "east", "type": "drain", "offset": 1000}],
        "existing_electrical": [{"wall": "south", "offset": 1200}],
    },
    {
        "id": "plan_03_large_east_door",
        "description": "Large bathroom with east entry, multiple windows and flexible proposed infrastructure.",
        "room": {"width": 3600, "depth": 3000, "unit": "mm"},
        "door": {"wall": "east", "offset": 1000, "width": 900, "hinge_position": "top", "opening_direction": "outward", "swing_angle": 90, "swing_radius": 900},
        "windows": [{"wall": "north", "offset": 500, "width": 1200}, {"wall": "west", "offset": 700, "width": 800}],
        "ventilation": [{"wall": "south", "type": "exhaust_fan"}],
        "fixed_obstacles": [{"type": "service_chase", "x": 100, "y": 100, "width": 300, "depth": 900}],
        "existing_plumbing": [],
        "existing_electrical": [{"wall": "south", "offset": 1000}],
        "proposed_plumbing": [{"zone": "east_wall"}, {"zone": "south_wall"}],
        "proposed_electrical": [{"zone": "south_wall"}],
    },
    {
        "id": "plan_04_tiny_infeasible",
        "description": "Tiny bathroom intended to trigger spatial infeasibility in evaluation.",
        "room": {"width": 1200, "depth": 1500, "unit": "mm"},
        "door": {"wall": "south", "offset": 200, "width": 700, "hinge_position": "left", "opening_direction": "inward", "swing_angle": 90, "swing_radius": 700},
        "windows": [], "ventilation": [],
        "fixed_obstacles": [],
        "existing_plumbing": [{"wall": "west", "type": "water_supply", "offset": 300}],
        "existing_electrical": [],
    },
    {
        "id": "plan_05_missing_dimensions",
        "description": "Plan with visible door/window concepts but missing reliable room dimensions.",
        "room": {"width": None, "depth": None, "unit": "mm"},
        "door": {"wall": "south", "offset": 400, "width": 800, "hinge_position": "right", "opening_direction": "inward", "swing_angle": None, "swing_radius": None},
        "windows": [{"wall": "north", "offset": 500, "width": 900}],
        "ventilation": [], "fixed_obstacles": [],
        "existing_plumbing": [], "existing_electrical": [],
    },
    {
        "id": "plan_06_unknown_door_swing",
        "description": "Medium plan where door swing is deliberately unknown.",
        "room": {"width": 2200, "depth": 2600, "unit": "mm"},
        "door": {"wall": "west", "offset": 700, "width": 800, "hinge_position": None, "opening_direction": None, "swing_angle": None, "swing_radius": None},
        "windows": [{"wall": "east", "offset": 600, "width": 1000}],
        "ventilation": [{"wall": "north", "type": "exhaust_fan"}],
        "fixed_obstacles": [],
        "existing_plumbing": [{"wall": "south", "type": "drain", "offset": 700}],
        "existing_electrical": [{"wall": "north", "offset": 1200}],
    },
]

for scenario in scenarios:
    path = PLANS / f"{scenario['id']}.json"
    path.write_text(json.dumps(scenario, indent=2), encoding="utf-8")
    gold = {"room": scenario["room"], "door": scenario["door"], "windows": scenario["windows"]}
    (GOLD / f"{scenario['id']}_gold.json").write_text(json.dumps(gold, indent=2), encoding="utf-8")

print(f"Generated {len(scenarios)} synthetic evaluation plans")
