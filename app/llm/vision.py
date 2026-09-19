# """Multimodal bathroom-plan extraction with provenance and confidence."""

# from __future__ import annotations

# import json
# from pathlib import Path
# from typing import Any

# from pydantic import BaseModel, Field

# from app.llm.client import LLMError, LLMProvider, OpenAIProvider
# from app.models.spatial_plan import SpatialPlan


# class SpatialExtractionResult(BaseModel):
#     """Validated extraction plus explicit uncertainty/provisional status."""

#     spatial_plan: SpatialPlan
#     exact_layout_ready: bool = False
#     provisional_reasons: list[str] = Field(default_factory=list)
#     warnings: list[str] = Field(default_factory=list)


# class SpatialExtractor:
#     def __init__(self, provider: LLMProvider | None = None) -> None:
#         self.provider = provider or OpenAIProvider()

#     def extract(self, image_path: str | Path) -> SpatialExtractionResult:
#         payload = self.provider.generate_json(
#             system_prompt=_load_prompt("spatial_extraction.txt"),
#             user_prompt=(
#                 "Extract the bathroom spatial plan from the supplied image. "
#                 "Return only JSON matching the requested structure. Never infer a precise "
#                 "dimension when it is not supported by an annotation, reliable scale, or "
#                 "user-provided information. Use null with source=unknown when unavailable."
#             ),
#             image_path=image_path,
#             schema_name="spatial extraction",
#         )
#         return validate_spatial_payload(payload)


# def validate_spatial_payload(payload: dict[str, Any]) -> SpatialExtractionResult:
#     """Validate and normalize model output before it reaches geometry code."""
#     try:
#         spatial_payload = payload.get("spatial_plan", payload)
#         plan = SpatialPlan.model_validate(spatial_payload)
#     except Exception as exc:
#         raise LLMError(f"Malformed spatial plan: {exc}") from exc

#     reasons: list[str] = []
#     warnings: list[str] = []
#     if plan.room_width.value is None or plan.room_depth.value is None:
#         reasons.append("Exact room dimensions are missing; layout is provisional.")
#     if plan.door is None:
#         reasons.append("Door information is missing; door validation is provisional.")
#     elif plan.door.swing is None or plan.door.swing.direction is None:
#         reasons.append("Door swing direction is unknown; door-swing validation is provisional.")
#     if plan.door and plan.door.swing:
#         if plan.door.swing.swing_radius and plan.door.swing.swing_radius.value is None:
#             warnings.append("Door swing radius is unavailable.")
#     for label, collection in (
#         ("window", plan.windows),
#         ("ventilation", plan.ventilation),
#         ("fixed obstacle", plan.fixed_obstacles),
#     ):
#         if not collection:
#             warnings.append(f"No {label} was confidently identified; verify the source plan if relevant.")

#     # Explicitly preserve the model's uncertainty rather than manufacturing geometry.
#     return SpatialExtractionResult(
#         spatial_plan=plan,
#         exact_layout_ready=not reasons,
#         provisional_reasons=reasons,
#         warnings=warnings,
#     )


# def extraction_to_json(result: SpatialExtractionResult) -> str:
#     return json.dumps(result.model_dump(mode="json"), indent=2)


# def _load_prompt(filename: str) -> str:
#     path = Path(__file__).parent / "prompts" / filename
#     return path.read_text(encoding="utf-8")


"""Multimodal bathroom-plan extraction with provenance and confidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.llm.client import LLMError, LLMProvider, GroqProvider
from app.models.spatial_plan import SpatialPlan


class SpatialExtractionResult(BaseModel):
    """Validated extraction plus explicit uncertainty/provisional status."""

    spatial_plan: SpatialPlan
    exact_layout_ready: bool = False
    provisional_reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class SpatialExtractor:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider or GroqProvider()

    def extract(self, image_path: str | Path) -> SpatialExtractionResult:
        payload = self.provider.generate_json(
            system_prompt=_load_prompt("spatial_extraction.txt"),
            user_prompt=(
                "Extract the bathroom spatial plan from the supplied image. "
                "Return only JSON matching the requested structure. Never infer a precise "
                "dimension when it is not supported by an annotation, reliable scale, or "
                "user-provided information. Use null with source=unknown when unavailable."
            ),
            image_path=image_path,
            schema_name="spatial extraction",
        )
        return validate_spatial_payload(payload)


def validate_spatial_payload(
    payload: dict[str, Any],
) -> SpatialExtractionResult:
    """Validate and normalize model output before it reaches geometry code."""

    try:
        spatial_payload = payload.get("spatial_plan", payload)
        plan = SpatialPlan.model_validate(spatial_payload)

    except Exception as exc:
        raise LLMError(f"Malformed spatial plan: {exc}") from exc

    reasons: list[str] = []
    warnings: list[str] = []

    if plan.room_width.value is None or plan.room_depth.value is None:
        reasons.append(
            "Exact room dimensions are missing; layout is provisional."
        )

    if plan.door is None:
        reasons.append(
            "Door information is missing; door validation is provisional."
        )

    elif plan.door.swing is None or plan.door.swing.direction is None:
        reasons.append(
            "Door swing direction is unknown; door-swing validation is provisional."
        )

    if plan.door and plan.door.swing:
        if (
            plan.door.swing.swing_radius
            and plan.door.swing.swing_radius.value is None
        ):
            warnings.append("Door swing radius is unavailable.")

    for label, collection in (
        ("window", plan.windows),
        ("ventilation", plan.ventilation),
        ("fixed obstacle", plan.fixed_obstacles),
    ):
        if not collection:
            warnings.append(
                f"No {label} was confidently identified; "
                "verify the source plan if relevant."
            )

    # Explicitly preserve the model's uncertainty rather than manufacturing geometry.
    return SpatialExtractionResult(
        spatial_plan=plan,
        exact_layout_ready=not reasons,
        provisional_reasons=reasons,
        warnings=warnings,
    )


def extraction_to_json(result: SpatialExtractionResult) -> str:
    return json.dumps(
        result.model_dump(mode="json"),
        indent=2,
    )


def _load_prompt(filename: str) -> str:
    path = Path(__file__).parent / "prompts" / filename
    return path.read_text(encoding="utf-8")

