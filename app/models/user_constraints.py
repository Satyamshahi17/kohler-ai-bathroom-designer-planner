"""User requirements normalized into a structured, testable contract."""

from pydantic import BaseModel, Field


class UserConstraints(BaseModel):
    budget: float = Field(ge=0)
    theme: str = ""
    required_categories: list[str] = Field(default_factory=list)
    preferences: list[str] = Field(default_factory=list)
    room_requirements: dict[str, object] = Field(default_factory=dict)
    door_preferences: dict[str, object] = Field(default_factory=dict)
