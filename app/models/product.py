"""Structured product model used between catalog, KG, recommendation and optimization."""

from pydantic import BaseModel, Field


class Product(BaseModel):
    id: str
    model_number: str
    name: str
    category: str
    price: float = Field(ge=0)
    width: float = Field(gt=0)
    depth: float = Field(gt=0)
    height: float = Field(gt=0)
    description: str = ""
    style_tags: list[str] = Field(default_factory=list)
    finish: str | None = None
    installation_type: str | None = None
    faucet_configuration: str | None = None
    clearance_requirements: dict[str, float] = Field(default_factory=dict)
    infrastructure_requirements: list[str] = Field(default_factory=list)
    required_accessories: list[str] = Field(default_factory=list)
    compatibility: list[str] = Field(default_factory=list)
