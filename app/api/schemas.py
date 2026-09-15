"""Small request/response helpers for the Flask API."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.models.spatial_plan import SpatialPlan


class DesignRequest(BaseModel):
    requirements: str = Field(min_length=1)
    spatial_plan: SpatialPlan | None = None
    top_k: int = Field(default=3, ge=1, le=3)


class ReplaceRequest(BaseModel):
    category: str = Field(min_length=1)
    requirements: str | None = None
    spatial_plan: SpatialPlan | None = None
    result: dict[str, Any]
