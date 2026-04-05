from __future__ import annotations

import json
from typing import Any

from openrouter import OpenRouter

import config


def _extract_json(text: str) -> str:
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1]
            if text.startswith("json"):
                text = text[4:]
    return text.strip()


def generate_json(
    *,
    model: str,
    prompt: str,
    schema: dict[str, Any],
    temperature: float = 0.1,
    max_tokens: int = 400,
) -> dict[str, Any]:
    """Generate a JSON response via OpenRouter chat completions."""
    if not config.OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    schema_hint = json.dumps(schema, separators=(",", ":"))
    full_prompt = (
        f"{prompt}\n\n"
        "Return only valid JSON. Do not use markdown fences.\n"
        f"JSON schema: {schema_hint}"
    )

    with OpenRouter(api_key=config.OPENROUTER_API_KEY) as client:
        response = client.chat.send(
            model=model,
            messages=[{"role": "user", "content": full_prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )

    if not response.choices:
        raise ValueError("OpenRouter returned no choices")

    text = response.choices[0].message.content or ""
    if not text:
        raise ValueError("OpenRouter returned an empty response")

    return json.loads(_extract_json(text))
