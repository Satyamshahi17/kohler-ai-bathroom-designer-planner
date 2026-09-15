"""Spatial representation with provenance/confidence for extracted measurements."""

from typing import Literal

from pydantic import BaseModel, Field


class SourcedValue(BaseModel):
    value: float | str | bool | None
    unit: str | None = None
    source: Literal[
        "explicit_annotation",
        "image_scale",
        "user_provided",
        "approximation",
        "unknown",
    ] = "unknown"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class DoorSwing(BaseModel):
    direction: str | None = None
    angle: SourcedValue | None = None
    swing_radius: SourcedValue | None = None


class Door(BaseModel):
    wall: str | None = None
    offset: SourcedValue | None = None
    width: SourcedValue | None = None
    hinge_position: str | None = None
    opening_direction: str | None = None
    swing: DoorSwing | None = None


class SpatialPlan(BaseModel):
    room_width: SourcedValue
    room_depth: SourcedValue
    walls: list[dict[str, object]] = Field(default_factory=list)
    door: Door | None = None
    windows: list[dict[str, object]] = Field(default_factory=list)
    ventilation: list[dict[str, object]] = Field(default_factory=list)
    fixed_obstacles: list[dict[str, object]] = Field(default_factory=list)
    existing_plumbing: list[dict[str, object]] = Field(default_factory=list)
    existing_electrical: list[dict[str, object]] = Field(default_factory=list)
    proposed_plumbing: list[dict[str, object]] = Field(default_factory=list)
    proposed_electrical: list[dict[str, object]] = Field(default_factory=list)
