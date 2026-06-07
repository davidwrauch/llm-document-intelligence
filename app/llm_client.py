from __future__ import annotations

import json
import re
from typing import Any
from app.config import get_settings


class LLMClient:
    """Small provider wrapper. Mock mode is deterministic and requires no API key."""

    def __init__(self, provider: str | None = None):
        settings = get_settings()
        requested = (provider or settings.llm_provider or "mock").lower()

        if requested == "openai" and not settings.openai_api_key:
            requested = "mock"
        if requested == "anthropic" and not settings.anthropic_api_key:
            requested = "mock"
        if requested == "gemini" and not settings.gemini_api_key:
            requested = "mock"

        self.provider = requested
        self.settings = settings

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        text = text.strip()
        # Strip markdown fences if present
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return json.loads(text.strip() or "{}")

    def extract_json(self, prompt: str, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.provider == "openai":
            return self._openai_json(prompt)
        if self.provider == "anthropic":
            return self._anthropic_json(prompt)
        if self.provider == "gemini":
            return self._gemini_json(prompt)
        return fallback or {"provider": "mock", "confidence": 0.75}

    def _openai_json(self, prompt: str) -> dict[str, Any]:
        from openai import OpenAI

        client = OpenAI(api_key=self.settings.openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0,
        )
        return self._parse_json(response.choices[0].message.content or "{}")

    def _anthropic_json(self, prompt: str) -> dict[str, Any]:
        import anthropic

        client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            temperature=0,
            messages=[{"role": "user", "content": prompt + "\nReturn only valid JSON with no markdown fences."}],
        )
        text = "".join(block.text for block in response.content if hasattr(block, "text"))
        return self._parse_json(text)

    def _gemini_json(self, prompt: str) -> dict[str, Any]:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.settings.gemini_api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt + "\nReturn only valid JSON. Do not include markdown fences.",
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
            ),
        )
        return self._parse_json(response.text or "{}")
