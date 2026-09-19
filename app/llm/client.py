# """Provider abstraction for multimodal and structured LLM calls."""

# from __future__ import annotations

# import base64
# import json
# from pathlib import Path
# from typing import Any, Protocol

# from app.config.settings import settings


# class LLMError(RuntimeError):
#     """Raised when an LLM call cannot produce a usable structured result."""


# class LLMProvider(Protocol):
#     def generate_json(
#         self,
#         *,
#         system_prompt: str,
#         user_prompt: str,
#         image_path: str | Path | None = None,
#         schema_name: str = "response",
#     ) -> dict[str, Any]: ...


# class OpenAIProvider:
#     """Thin OpenAI Responses API adapter.

#     The dependency is imported lazily so the deterministic parts of the project
#     remain testable without an API key or network access.
#     """

#     def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
#         self.api_key = api_key or settings.openai_api_key
#         self.model = model or settings.openai_model

#     def generate_json(
#         self,
#         *,
#         system_prompt: str,
#         user_prompt: str,
#         image_path: str | Path | None = None,
#         schema_name: str = "response",
#     ) -> dict[str, Any]:
#         if not self.api_key:
#             raise LLMError("OPENAI_API_KEY is not configured")
#         try:
#             from openai import OpenAI
#         except ImportError as exc:
#             raise LLMError("The openai package is required for live LLM extraction") from exc

#         client = OpenAI(api_key=self.api_key)
#         content: list[dict[str, Any]] = [{"type": "input_text", "text": user_prompt}]
#         if image_path is not None:
#             path = Path(image_path)
#             if not path.is_file():
#                 raise LLMError(f"Image not found: {path}")
#             mime = _mime_type(path.suffix)
#             encoded = base64.b64encode(path.read_bytes()).decode("ascii")
#             content.append({
#                 "type": "input_image",
#                 "image_url": f"data:{mime};base64,{encoded}",
#             })

#         try:
#             response = client.responses.create(
#                 model=self.model,
#                 instructions=system_prompt,
#                 input=[{"role": "user", "content": content}],
#                 text={"format": {"type": "json_object"}},
#             )
#         except Exception as exc:  # SDK/provider errors vary by version.
#             raise LLMError(f"LLM request failed: {exc}") from exc

#         try:
#             payload = json.loads(response.output_text)
#         except (AttributeError, TypeError, json.JSONDecodeError) as exc:
#             raise LLMError(f"LLM returned malformed JSON for {schema_name}") from exc
#         if not isinstance(payload, dict):
#             raise LLMError(f"LLM returned a non-object JSON value for {schema_name}")
#         return payload


# def _mime_type(suffix: str) -> str:
#     return {
#         ".jpg": "image/jpeg",
#         ".jpeg": "image/jpeg",
#         ".png": "image/png",
#         ".webp": "image/webp",
#     }.get(suffix.lower(), "application/octet-stream")


"""Provider abstraction for multimodal and structured LLM calls."""

from __future__ import annotations

import base64
import json
import mimetypes
from pathlib import Path
from typing import Any, Protocol

from app.config.settings import settings


class LLMError(RuntimeError):
    """Raised when an LLM call cannot produce a usable structured result."""


class LLMProvider(Protocol):
    def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        image_path: str | Path | None = None,
        schema_name: str = "response",
    ) -> dict[str, Any]:
        ...


class GroqProvider:
    """Thin Groq adapter for multimodal and structured LLM calls.

    Uses Groq-hosted Qwen 3.8 27B for text + image understanding.
    The dependency is imported lazily so deterministic parts of the project
    remain testable without an API key or network access.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or settings.groq_api_key
        self.model = model or settings.groq_model

    def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        image_path: str | Path | None = None,
        schema_name: str = "response",
    ) -> dict[str, Any]:
        if not self.api_key:
            raise LLMError("GROQ_API_KEY is not configured")

        try:
            from groq import Groq
        except ImportError as exc:
            raise LLMError(
                "The groq package is required for live LLM extraction"
            ) from exc

        client = Groq(api_key=self.api_key)

        user_content: list[dict[str, Any]] = [
            {
                "type": "text",
                "text": user_prompt,
            }
        ]

        if image_path is not None:
            path = Path(image_path)

            if not path.is_file():
                raise LLMError(f"Image not found: {path}")

            mime_type, _ = mimetypes.guess_type(path.name)

            if mime_type not in {
                "image/jpeg",
                "image/png",
                "image/webp",
            }:
                raise LLMError(
                    f"Unsupported image type: {path.suffix}"
                )

            encoded = base64.b64encode(
                path.read_bytes()
            ).decode("ascii")

            user_content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{encoded}"
                    },
                }
            )

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_content,
                    },
                ],
                response_format={
                    "type": "json_object",
                },
                reasoning_effort="none",
                temperature=0.2,
                max_completion_tokens=2048,
            )
        except Exception as exc:
            raise LLMError(
                f"LLM request failed: {exc}"
            ) from exc

        try:
            output_text = response.choices[0].message.content
            payload = json.loads(output_text)
        except (
            AttributeError,
            IndexError,
            TypeError,
            json.JSONDecodeError,
        ) as exc:
            raise LLMError(
                f"LLM returned malformed JSON for {schema_name}"
            ) from exc

        if not isinstance(payload, dict):
            raise LLMError(
                f"LLM returned a non-object JSON value for {schema_name}"
            )

        return payload

