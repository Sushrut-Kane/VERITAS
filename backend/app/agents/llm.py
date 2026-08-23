"""Async LLM wrapper supporting Groq and Anthropic with tenacity retries and JSON parsing.

Centralizes the LLM call sites (extraction, evidence-sufficiency, classification).
When no API key is configured, ``complete`` raises and callers fall back to
deterministic logic — keeping the pipeline runnable offline for tests and demos.
"""
import json
from functools import lru_cache
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LLMUnavailableError(RuntimeError):
    """Raised when an LLM call is attempted but no API key is configured."""


@lru_cache
def _anthropic_client() -> Any:
    from anthropic import AsyncAnthropic

    return AsyncAnthropic(api_key=settings.anthropic_api_key)


async def _complete_groq(
    system: str,
    user_content: str | list[dict[str, Any]],
    *,
    max_tokens: int | None = None,
) -> str:
    messages = [{"role": "system", "content": system}]
    if isinstance(user_content, str):
        messages.append({"role": "user", "content": user_content})
    else:
        messages.append({"role": "user", "content": str(user_content)})

    payload = {
        "model": settings.groq_model,
        "messages": messages,
        "temperature": 0,
        "max_tokens": max_tokens or settings.llm_max_tokens,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        res = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.groq_api_key}"},
            json=payload,
        )
        if res.status_code != 200:
            logger.error("groq_error", status_code=res.status_code, body=res.text)
            raise RuntimeError(f"Groq API error ({res.status_code}): {res.text}")
        data = res.json()
        usage = data.get("usage")
        if usage:
            logger.info(
                "llm_usage",
                input_tokens=usage.get("prompt_tokens"),
                output_tokens=usage.get("completion_tokens"),
            )
        return data["choices"][0]["message"]["content"] or ""


async def _complete_anthropic(
    system: str,
    user_content: str | list[dict[str, Any]],
    *,
    max_tokens: int | None = None,
) -> str:
    if isinstance(user_content, str):
        messages = [{"role": "user", "content": user_content}]
    else:
        messages = [{"role": "user", "content": user_content}]

    response = await _anthropic_client().messages.create(
        model=settings.anthropic_model,
        max_tokens=max_tokens or settings.llm_max_tokens,
        temperature=0,
        system=system,
        messages=messages,
    )
    usage = getattr(response, "usage", None)
    if usage is not None:
        logger.info(
            "llm_usage",
            input_tokens=getattr(usage, "input_tokens", None),
            output_tokens=getattr(usage, "output_tokens", None),
        )

    parts: list[str] = []
    for block in response.content:
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
    return "".join(parts)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
async def complete(
    system: str,
    user_content: str | list[dict[str, Any]],
    *,
    max_tokens: int | None = None,
) -> str:
    """Call active LLM (Groq or Claude) and return text output."""
    if not settings.llm_enabled:
        raise LLMUnavailableError("Neither GROQ_API_KEY nor ANTHROPIC_API_KEY is configured")

    if settings.groq_api_key:
        return await _complete_groq(system, user_content, max_tokens=max_tokens)
    return await _complete_anthropic(system, user_content, max_tokens=max_tokens)


def parse_json_block(text: str) -> Any:
    """Extract a JSON value from a model response, tolerating ``` fences."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned[:4].lower() == "json":
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    for open_ch, close_ch in (("[", "]"), ("{", "}")):
        start, end = cleaned.find(open_ch), cleaned.rfind(close_ch)
        if start != -1 and end > start:
            try:
                return json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError(f"No JSON found in LLM response: {text[:200]!r}")
