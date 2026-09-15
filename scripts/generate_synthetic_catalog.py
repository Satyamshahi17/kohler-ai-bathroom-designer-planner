"""Generate a deterministic synthetic bathroom catalog for development/evaluation."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "app" / "products" / "data" / "synthetic_products.json"

styles = [
    ("Japanese Zen", ["japanese-zen", "warm", "minimal"]),
    ("Modern", ["modern", "minimal", "clean"]),
    ("Organic Spa", ["spa", "organic", "warm"]),
    ("Contemporary", ["contemporary", "refined"]),
    ("Classic", ["classic", "timeless"]),
]
finishes = ["Natural Oak", "Matte White", "Brushed Nickel", "Matte Black", "Polished Chrome"]

products = []

def add(category, i, name, price, w, d, h, tags, finish, install, desc, accessories=None, infra=None, clearance=None, faucet=None, compatibility=None):
    products.append({
        "id": f"SYN-{category[:3].upper()}-{i:03d}",
        "model_number": f"SYN-{category[:3].upper()}-{i:03d}",
        "name": name,
        "category": category,
        "price": price,
        "width": w,
        "depth": d,
        "height": h,
        "description": desc,
        "style_tags": tags,
        "finish": finish,
        "installation_type": install,
        "faucet_configuration": faucet,
        "clearance_requirements": clearance or {"front": 600, "side": 150},
        "infrastructure_requirements": infra or [],
        "required_accessories": accessories or [],
        "compatibility": compatibility or [],
    })

for i in range(1, 26):
    theme, tags = styles[(i - 1) % len(styles)]
    add("vanity", i, f"{theme} Vanity {i:02d}", 650 + i * 55, 600 + (i % 6) * 100, 450 + (i % 4) * 40, 550 + (i % 3) * 30, tags, finishes[(i - 1) % len(finishes)], "wall_mounted" if i % 2 else "floor_mounted", f"Synthetic {theme.lower()} vanity for research evaluation.", ["SYN-ACC-001" if i % 3 == 0 else "SYN-ACC-002"], ["water_supply", "drain"])

for i in range(1, 26):
    theme, tags = styles[(i + 1) % len(styles)]
    faucet = "single-hole" if i % 2 else "widespread"
    add("faucet", i, f"{theme} Faucet {i:02d}", 180 + i * 18, 80, 180 + (i % 3) * 20, 280 + (i % 4) * 25, tags, finishes[(i + 2) % len(finishes)], "deck_mounted", f"Synthetic {theme.lower()} faucet with {faucet} configuration.", ["SYN-ACC-003"], ["water_supply"], {"front": 300, "side": 100}, faucet=faucet)

for i in range(1, 26):
    theme, tags = styles[(i + 2) % len(styles)]
    install = "wall_hung" if i % 3 == 0 else "floor_mounted"
    infra = ["water_supply", "drain"] + (["electrical"] if i in (8, 18) else [])
    acc = ["SYN-ACC-004"] + (["SYN-ACC-005"] if i in (8, 18) else [])
    add("toilet", i, f"{theme} Toilet {i:02d}", 700 + i * 48, 360 + (i % 3) * 20, 650 + (i % 4) * 25, 700 + (i % 2) * 30, tags, finishes[(i + 1) % len(finishes)], install, f"Synthetic {theme.lower()} toilet.", acc, infra, {"front": 750, "side": 150})

for i in range(1, 26):
    theme, tags = styles[(i + 3) % len(styles)]
    infra = ["water_supply", "drain"] + (["electrical"] if i in (7, 17) else [])
    acc = ["SYN-ACC-006"] + (["SYN-ACC-005"] if i in (7, 17) else [])
    add("shower", i, f"{theme} Shower {i:02d}", 900 + i * 65, 800 + (i % 4) * 100, 800 + (i % 3) * 100, 2100, tags, finishes[(i + 3) % len(finishes)], "wall_mounted", f"Synthetic {theme.lower()} shower system.", acc, infra, {"front": 700, "side": 100})

for i in range(1, 21):
    names = ["Bottle Shelf", "Towel Bar", "Mirror", "Robe Hook", "Drain Cover"]
    add("accessory", i, f"{names[(i-1)%5]} {i:02d}", 45 + i * 9, 100 + (i % 4) * 50, 40 + (i % 3) * 20, 100 + (i % 5) * 30, ["minimal", "functional"], finishes[(i + 4) % len(finishes)], "wall_mounted", "Synthetic bathroom accessory.", infra=["electrical"] if i == 20 else [])

# Deliberately adversarial but still valid records.
# Cheap + incompatible with a widespread-only vanity/faucet pairing is represented by explicit references.
products[0]["compatibility"] = [products[25]["id"]]
products[25]["compatibility"] = [products[0]["id"]]
products[1]["width"] = 2200  # visually attractive but often too large for small evaluation rooms.
products[17]["required_accessories"] = ["SYN-ACC-005"]  # expensive infrastructure accessory case.
products[49]["price"] = 4900  # budget-stress product.

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(products, indent=2), encoding="utf-8")
print(f"Wrote {len(products)} products to {OUT}")
