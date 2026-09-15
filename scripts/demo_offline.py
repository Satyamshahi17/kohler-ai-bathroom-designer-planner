"""Run the deterministic demo path using a synthetic structured bathroom plan.

Requires the project dependencies. No image API call is made.
"""
from __future__ import annotations

import json
from pathlib import Path

from app.llm.vision import validate_spatial_payload
from app.pipeline.orchestrator import DesignPipeline


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    plan_path = root / "evaluation" / "bathroom_plans" / "plan_02_medium_north_door.json"
    payload = json.loads(plan_path.read_text(encoding="utf-8"))
    plan = validate_spatial_payload({"spatial_plan": payload}).spatial_plan
    result = DesignPipeline().run(
        requirements="I want a warm Japanese Zen bathroom under $5000 with vanity, faucet, toilet and shower.",
        spatial_plan=plan,
    )
    print(json.dumps(result.model_dump(mode="json"), indent=2))
    return 0 if result.status in {"success", "provisional", "no_valid_layout"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
