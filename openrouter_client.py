from __future__ import annotations

import json
import time
from typing import Any

from openrouter import OpenRouter
from openrouter import utils as openrouter_utils
from openrouter.errors import (
    BadGatewayResponseError,
    EdgeNetworkTimeoutResponseError,
    InternalServerResponseError,
    OpenRouterDefaultError,
    ProviderOverloadedResponseError,
    RequestTimeoutResponseError,
    ResponseValidationError,
    ServiceUnavailableResponseError,
    TooManyRequestsResponseError,
)

import config

RETRYABLE_ERRORS = (
    BadGatewayResponseError,
    EdgeNetworkTimeoutResponseError,
    InternalServerResponseError,
    OpenRouterDefaultError,
    ProviderOverloadedResponseError,
    RequestTimeoutResponseError,
    ResponseValidationError,
    ServiceUnavailableResponseError,
    TooManyRequestsResponseError,
)

RETRY_CONFIG = openrouter_utils.RetryConfig(
    strategy="backoff",
    backoff=openrouter_utils.BackoffStrategy(
        initial_interval=250,
        max_interval=2000,
        exponent=2.0,
        max_elapsed_time=5000,
    ),
    retry_connection_errors=True,
)


def _extract_json(text: str) -> str:
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1]
            if text.startswith("json"):
                text = text[4:]
    text = text.strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end >= start:
        return text[start:end + 1]
    return text


def _normalize_message(err: Exception) -> str:
    raw_message = str(err).strip()
    body = getattr(err, "body", "") or ""

    if body:
        try:
            parsed = json.loads(body)
            if isinstance(parsed, dict):
                error = parsed.get("error")
                if isinstance(error, dict):
                    message = error.get("message") or error.get("metadata", {}).get("raw")
                    if message:
                        raw_message = str(message)
        except Exception:
            pass

    raw_message = " ".join(raw_message.split())
    return raw_message[:240]


def _should_retry(err: Exception) -> bool:
    if isinstance(err, RETRYABLE_ERRORS):
        if isinstance(err, OpenRouterDefaultError):
            status = getattr(err, "status_code", 0)
            return status >= 500 or status == 429
        if isinstance(err, ResponseValidationError):
            raw_response = getattr(err, "raw_response", None)
            if raw_response is not None and raw_response.status_code >= 500:
                return True
            body = getattr(err, "body", "") or ""
            return "\"code\": 502" in body or "Upstream provider error" in body
        return True
    return False


def generate_json(
    *,
    model: str,
    prompt: str,
    schema: dict[str, Any],
    temperature: float = 0.1,
    max_tokens: int = 400,
    max_attempts: int = 3,
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

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            with OpenRouter(api_key=config.OPENROUTER_API_KEY) as client:
                response = client.chat.send(
                    model=model,
                    messages=[{"role": "user", "content": full_prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    retries=RETRY_CONFIG,
                    timeout_ms=30000,
                )

            if not response.choices:
                raise ValueError("OpenRouter returned no choices")

            text = response.choices[0].message.content or ""
            if not text:
                raise ValueError("OpenRouter returned an empty response")

            return json.loads(_extract_json(text))

        except json.JSONDecodeError as err:
            last_error = err
            if attempt >= max_attempts:
                break
        except Exception as err:
            last_error = err
            if not _should_retry(err) or attempt >= max_attempts:
                raise RuntimeError(_normalize_message(err)) from err

        time.sleep(min(0.5 * attempt, 1.5))

    if last_error is None:
        raise RuntimeError("OpenRouter request failed")
    raise RuntimeError(_normalize_message(last_error)) from last_error
