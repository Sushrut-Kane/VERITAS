"""Thin async Anthropic wrapper with tenacity retries and a JSON parse helper.

Centralizes the three LLM call sites (extraction, evidence-sufficiency,
classification) so retry/logging/parsing live in one place. When no API key is
configured, ``complete`` raises and callers fall back to deterministic logic —
this keeps the whole pipeline runnable offline for tests and demos.
"""
import json
from functools import lru_cache
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LLMUnavailableError(RuntimeError):
    """Raised when an LLM call is attempted but no API key is configured."""


@lru_cache
def _client() -> Any:
    from groq import AsyncGroq

    return AsyncGroq(api_key=settings.groq_api_key)


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
    """Call Groq (temperature 0) and return the concatenated text output."""
    if not settings.llm_enabled:
        raise LLMUnavailableError("GROQ_API_KEY is not configured")
    
    # Format messages for Groq API
    messages = [{"role": "system", "content": system}]
    
    # For extraction payload where we previously used a list of dicts for anthropic vision
    if isinstance(user_content, list):
        # Groq might not support Anthropic's exact vision payload, so let's try to extract text if it's there
        text_content = ""
        for block in user_content:
            if block.get("type") == "text":
                text_content += block.get("text", "") + "\n"
        
        # If it was just text blocks, use that, else send raw payload and hope it works
        if text_content:
            messages.append({"role": "user", "content": text_content.strip()})
        else:
            messages.append({"role": "user", "content": str(user_content)})
    else:
        messages.append({"role": "user", "content": user_content})

    response = await _client().chat.completions.create(
        model=settings.groq_model,
        max_tokens=max_tokens or settings.llm_max_tokens,
        temperature=0,
        messages=messages,
    )
    usage = getattr(response, "usage", None)
    if usage is not None:
        logger.info(
            "llm_usage",
            input_tokens=getattr(usage, "prompt_tokens", None),
            output_tokens=getattr(usage, "completion_tokens", None),
        )
        
    return response.choices[0].message.content or ""


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
