from __future__ import annotations

import json
from typing import Any

from google import genai

import config


def generate_json(
    *,
    model: str,
    prompt: str,
    schema: dict[str, Any],
    temperature: float = 0.1,
) -> dict[str, Any]:
    """Generate a structured JSON response from Gemini."""
    if not config.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set")

    client = genai.Client(api_key=config.GEMINI_API_KEY)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "temperature": temperature,
            "response_mime_type": "application/json",
            "response_json_schema": schema,
        },
    )

    text = (response.text or "").strip()
    if not text:
        raise ValueError("Gemini returned an empty response")

    return json.loads(text)
