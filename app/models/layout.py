"""Layout data contract. Geometry implementation arrives in later phases."""

from pydantic import BaseModel, Field


class FixturePlacement(BaseModel):
    product_id: str
    category: str
    x: float
    y: float
    rotation: float = 0.0


class Layout(BaseModel):
    id: str
    room_width: float
    room_depth: float
    fixtures: list[FixturePlacement] = Field(default_factory=list)
    strategy: str = ""
