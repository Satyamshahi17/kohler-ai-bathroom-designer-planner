# """Natural-language user requirement parsing into deterministic constraints."""

# from __future__ import annotations

# import re
# from typing import Any

# from app.llm.client import LLMError, LLMProvider, OpenAIProvider
# from app.models.user_constraints import UserConstraints


# class RequirementsParser:
#     def __init__(self, provider: LLMProvider | None = None) -> None:
#         self.provider = provider or OpenAIProvider()

#     def parse(self, text: str) -> UserConstraints:
#         if not text.strip():
#             raise ValueError("User requirements cannot be empty")
#         try:
#             payload = self.provider.generate_json(
#                 system_prompt=_load_prompt("requirements.txt"),
#                 user_prompt=text,
#                 schema_name="requirements",
#             )
#             return UserConstraints.model_validate(payload)
#         except LLMError:
#             # Local fallback is intentionally conservative and only extracts
#             # unambiguous constraints. It never invents a budget or category.
#             return parse_basic_requirements(text)


# def parse_basic_requirements(text: str) -> UserConstraints:
#     lower = text.lower()
#     budget_match = re.search(r"(?:\$|usd\s*)\s*([\d,]+(?:\.\d+)?)", lower)
#     if budget_match is None:
#         budget_match = re.search(r"(?:under|below|budget(?:\s+of)?)\s+([\d,]+(?:\.\d+)?)", lower)
#     budget = float(budget_match.group(1).replace(",", "")) if budget_match else 0.0

#     categories = [
#         category for category in ("vanity", "faucet", "toilet", "shower", "accessory")
#         if category in lower
#     ]
#     theme = ""
#     for candidate in ("japanese zen", "modern", "minimalist", "traditional", "industrial", "spa"):
#         if candidate in lower:
#             theme = candidate.title()
#             break

#     preferences = [
#         word for word in ("warm", "minimal", "spa-like", "organic", "natural", "wall-mounted")
#         if word in lower
#     ]
#     return UserConstraints(
#         budget=budget,
#         theme=theme,
#         required_categories=list(dict.fromkeys(categories)),
#         preferences=preferences,
#     )


# def _load_prompt(filename: str) -> str:
#     from pathlib import Path

#     return (Path(__file__).parent / "prompts" / filename).read_text(encoding="utf-8")

"""Natural-language user requirement parsing into deterministic constraints."""

from __future__ import annotations

import re
from typing import Any

from app.llm.client import LLMError, LLMProvider, GroqProvider
from app.models.user_constraints import UserConstraints


class RequirementsParser:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider or GroqProvider()

    def parse(self, text: str) -> UserConstraints:
        if not text.strip():
            raise ValueError("User requirements cannot be empty")

        try:
            payload = self.provider.generate_json(
                system_prompt=_load_prompt("requirements.txt"),
                user_prompt=text,
                schema_name="requirements",
            )
            return UserConstraints.model_validate(payload)

        except LLMError:
            # Local fallback is intentionally conservative and only extracts
            # unambiguous constraints. It never invents a budget or category.
            return parse_basic_requirements(text)


def parse_basic_requirements(text: str) -> UserConstraints:
    lower = text.lower()

    budget_match = re.search(
        r"(?:\$|usd\s*)\s*([\d,]+(?:\.\d+)?)",
        lower,
    )

    if budget_match is None:
        budget_match = re.search(
            r"(?:under|below|budget(?:\s+of)?)\s+([\d,]+(?:\.\d+)?)",
            lower,
        )

    budget = (
        float(budget_match.group(1).replace(",", ""))
        if budget_match
        else 0.0
    )

    categories = [
        category
        for category in (
            "vanity",
            "faucet",
            "toilet",
            "shower",
            "accessory",
        )
        if category in lower
    ]

    theme = ""

    for candidate in (
        "japanese zen",
        "modern",
        "minimalist",
        "traditional",
        "industrial",
        "spa",
    ):
        if candidate in lower:
            theme = candidate.title()
            break

    preferences = [
        word
        for word in (
            "warm",
            "minimal",
            "spa-like",
            "organic",
            "natural",
            "wall-mounted",
        )
        if word in lower
    ]

    return UserConstraints(
        budget=budget,
        theme=theme,
        required_categories=list(dict.fromkeys(categories)),
        preferences=preferences,
    )


def _load_prompt(filename: str) -> str:
    from pathlib import Path

    return (
        Path(__file__).parent / "prompts" / filename
    ).read_text(encoding="utf-8")

