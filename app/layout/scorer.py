"""Scoring for already-valid layout candidates."""
from __future__ import annotations

from app.models.layout import Layout


class LayoutScorer:
    def score(self, layout: Layout, validation: dict[str, object],
              theme: str = "", preferences: list[str] | None = None) -> dict[str, float]:
        if not validation.get("valid", False):
            return {"total": 0.0, "feasibility": 0.0, "space_efficiency": 0.0,
                    "circulation": 0.0, "aesthetic": 0.0, "preference": 0.0}
        room_area = layout.room_width * layout.room_depth
        used = 0.0
        for f in layout.fixtures:
            # Product areas aren't available in the layout model, so this component
            # is supplied by selector when richer product data is available.
            used += 1.0
        space_efficiency = max(0.0, 1.0 - used / max(room_area / 100000.0, 1.0))
        aesthetic = 0.75 if theme else 0.5
        preference = 0.5 + min(len(preferences or []), 5) * 0.05
        circulation = 1.0 if not any(v.get("type") == "CIRCULATION" for v in validation.get("violations", [])) else 0.0
        total = 0.30 + 0.20 * space_efficiency + 0.20 * circulation + 0.15 * aesthetic + 0.15 * preference
        return {"total": round(total, 4), "feasibility": 1.0,
                "space_efficiency": round(space_efficiency, 4),
                "circulation": circulation, "aesthetic": aesthetic,
                "preference": preference}
