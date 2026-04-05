"""
Gemini classification engine that replaces probability estimation with
direction classification.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import config
from gemini_client import generate_json
from markets import Market

log = logging.getLogger(__name__)

CLASSIFICATION_PROMPT = """You are a news classifier for prediction markets.

## Market Question
{question}

## Current Market Price
YES: {yes_price:.2f} (implied probability: {yes_price:.0%})

## Breaking News
{headline}
Source: {source}

## Task
Does this news make the market question MORE likely to resolve YES, MORE likely to resolve NO, or is it NOT RELEVANT?

Also rate the MATERIALITY. 0.0 means no impact, 1.0 means this is definitive evidence.

Respond with ONLY valid JSON:
{{
  "direction": "bullish" | "bearish" | "neutral",
  "materiality": <float 0.0 to 1.0>,
  "reasoning": "<1 sentence>"
}}"""

CLASSIFICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "direction": {
            "type": "string",
            "enum": ["bullish", "bearish", "neutral"],
        },
        "materiality": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
        },
        "reasoning": {"type": "string"},
    },
    "required": ["direction", "materiality", "reasoning"],
}


@dataclass
class Classification:
    direction: str  # "bullish", "bearish", "neutral"
    materiality: float  # 0.0-1.0
    reasoning: str
    latency_ms: int
    model: str


def classify(headline: str, market: Market, source: str = "unknown") -> Classification:
    """Classify a news headline against a market question."""
    start = time.time()

    prompt = CLASSIFICATION_PROMPT.format(
        question=market.question,
        yes_price=market.yes_price,
        headline=headline,
        source=source,
    )

    try:
        result = generate_json(
            model=config.CLASSIFICATION_MODEL,
            prompt=prompt,
            schema=CLASSIFICATION_SCHEMA,
            temperature=0.1,
        )
        latency = int((time.time() - start) * 1000)

        direction = result.get("direction", "neutral")
        if direction not in ("bullish", "bearish", "neutral"):
            direction = "neutral"

        materiality = max(0.0, min(1.0, float(result.get("materiality", 0.0))))

        return Classification(
            direction=direction,
            materiality=materiality,
            reasoning=str(result.get("reasoning", "")),
            latency_ms=latency,
            model=config.CLASSIFICATION_MODEL,
        )

    except Exception as e:
        latency = int((time.time() - start) * 1000)
        log.warning(f"[classifier] Error: {e}")
        return Classification(
            direction="neutral",
            materiality=0.0,
            reasoning=f"Classification error: {type(e).__name__}",
            latency_ms=latency,
            model=config.CLASSIFICATION_MODEL,
        )


async def classify_async(headline: str, market: Market, source: str = "unknown") -> Classification:
    """Async wrapper around classify()."""
    import asyncio

    return await asyncio.get_event_loop().run_in_executor(
        None, classify, headline, market, source
    )


if __name__ == "__main__":
    test_market = Market(
        condition_id="test",
        question="Will OpenAI release GPT-5 before August 2026?",
        category="ai",
        yes_price=0.62,
        no_price=0.38,
        volume=500000,
        end_date="2026-08-01",
        active=True,
        tokens=[],
    )

    result = classify(
        headline="OpenAI reportedly testing GPT-5 internally with select partners",
        market=test_market,
        source="The Information",
    )
    print(f"Direction: {result.direction}")
    print(f"Materiality: {result.materiality}")
    print(f"Reasoning: {result.reasoning}")
    print(f"Latency: {result.latency_ms}ms")
