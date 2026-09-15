"""Top-level result contract for the eventual end-to-end pipeline."""

from typing import Any

from pydantic import BaseModel, Field

from .layout import Layout
from .spatial_plan import SpatialPlan


class DesignResult(BaseModel):
    status: str
    spatial_plan: SpatialPlan | None = None
    bundle: dict[str, Any] = Field(default_factory=dict)
    alternatives: list[dict[str, Any]] = Field(default_factory=list)
    layout: Layout | None = None
    svg: str | None = None
    validation: dict[str, Any] = Field(default_factory=dict)
    explanation: dict[str, Any] = Field(default_factory=dict)
    trace: list[dict[str, Any]] = Field(default_factory=list)
