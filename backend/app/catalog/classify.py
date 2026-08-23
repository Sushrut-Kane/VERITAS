"""Taxonomy classification: map a part description to a UniLog classpath.

Two-tier strategy (stdlib-only unless a pgvector session is supplied):

1. When ``candidates`` exist and ``session`` is provided, rank classpaths by
   pgvector cosine similarity against hash-stored reference vectors (see
   ``reference_lookup``).
2. Below the confidence threshold, or when no session is available, fall back to
   keyword-overlap against the candidate classpath strings.

Never invents a classpath string from scratch — returns ``("", 0.0)`` when
nothing matches (honest blank, same as other enrich gaps).
"""
from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

CONFIDENCE_THRESHOLD = 0.35

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    return set(_TOKEN_RE.findall(text.lower()))


def _token_overlap(desc_tokens: set[str], cp_tokens: set[str]) -> int:
    overlap = len(desc_tokens & cp_tokens)
    for ta in desc_tokens:
        for tb in cp_tokens:
            if ta == tb:
                continue
            if min(len(ta), len(tb)) >= 3 and (ta.startswith(tb) or tb.startswith(ta)):
                overlap += 1
                break
    return overlap


def _keyword_overlap_score(part_desc: str, classpath: str) -> float:
    desc_tokens = _tokens(part_desc)
    cp_text = classpath.replace("/", " ").replace("_", " ")
    cp_tokens = _tokens(cp_text)
    if not desc_tokens or not cp_tokens:
        return 0.0
    overlap = _token_overlap(desc_tokens, cp_tokens)
    if overlap == 0:
        return 0.0
    return overlap / math.sqrt(len(desc_tokens) * len(cp_tokens))


def _best_keyword_match(part_desc: str, candidates: list[str]) -> tuple[str, float]:
    best_cp = ""
    best_score = 0.0
    for cp in candidates:
        if not cp:
            continue
        score = _keyword_overlap_score(part_desc, cp)
        if score > best_score:
            best_score = score
            best_cp = cp
    return best_cp, best_score


async def _pgvector_match(
    session: AsyncSession, part_desc: str, candidates: list[str]
) -> tuple[str, float]:
    """Best classpath by pgvector similarity when reference embeddings exist."""
    from app.catalog.reference_lookup import classpath_embedding_match

    return await classpath_embedding_match(session, part_desc, candidates)


def classify_row(
    part_desc: str,
    part_manuf: str,
    candidates: list[str] | None = None,
    *,
    session: AsyncSession | None = None,
) -> tuple[str, float]:
    """Return ``(classpath, confidence)`` — sync entry uses keyword tier only."""
    del part_manuf, session

    if not candidates:
        return "", 0.0

    distinct = sorted({c.strip() for c in candidates if c and c.strip()})
    if not distinct:
        return "", 0.0

    cp, score = _best_keyword_match(part_desc, distinct)
    if score >= CONFIDENCE_THRESHOLD:
        return cp, score
    return "", 0.0


async def classify_row_async(
    part_desc: str,
    part_manuf: str,
    candidates: list[str] | None = None,
    *,
    session: AsyncSession | None = None,
) -> tuple[str, float]:
    """Async entry: pgvector tier first (when session set), then keyword fallback."""
    del part_manuf

    if not candidates:
        return "", 0.0

    distinct = sorted({c.strip() for c in candidates if c and c.strip()})
    if not distinct:
        return "", 0.0

    if session is not None:
        cp, score = await _pgvector_match(session, part_desc, distinct)
        if score >= CONFIDENCE_THRESHOLD:
            return cp, score

    cp, score = _best_keyword_match(part_desc, distinct)
    if score >= CONFIDENCE_THRESHOLD:
        return cp, score
    return "", 0.0
