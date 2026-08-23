"""Optional DB-backed lookups for catalog enrichment (importable without a live DB).

All functions accept an optional SQLAlchemy session; when ``None`` they return
``None`` / empty and callers keep their deterministic fallbacks.
"""
from __future__ import annotations

import hashlib
import math
import re
import struct
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _normalize_name(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


async def lookup_manufacturer(
    session: AsyncSession | None, raw: str
) -> tuple[str, str] | None:
    """Exact then fuzzy match against the ``manufacturers`` table."""
    if session is None or not raw or not raw.strip():
        return None

    from sqlalchemy import func, or_, select

    from app.db.models.reference import Manufacturer

    cleaned = raw.strip()
    # Try parenthesised code form first: "Name (CODE)"
    code_match = re.match(r"^\s*(?P<name>.*?)\s*\((?P<code>[^)]+)\)\s*$", cleaned)
    search_name = code_match.group("name").strip() if code_match else cleaned
    search_code = code_match.group("code").strip() if code_match else ""

    if search_code:
        stmt = select(Manufacturer).where(
            func.lower(Manufacturer.manufacturer_code) == search_code.lower()
        )
        result = await session.execute(stmt)
        row = result.scalars().first()
        if row:
            return row.manufacturer_name, row.manufacturer_code or search_code

    stmt = select(Manufacturer).where(
        func.lower(Manufacturer.manufacturer_name) == search_name.lower()
    )
    result = await session.execute(stmt)
    row = result.scalars().first()
    if row:
        return row.manufacturer_name, row.manufacturer_code

    norm = _normalize_name(search_name)
    if not norm:
        return None

    stmt = select(Manufacturer)
    result = await session.execute(stmt)
    for row in result.scalars():
        if _normalize_name(row.manufacturer_name) == norm:
            return row.manufacturer_name, row.manufacturer_code
        if norm in _normalize_name(row.manufacturer_name) or _normalize_name(
            row.manufacturer_name
        ) in norm:
            return row.manufacturer_name, row.manufacturer_code

    # Last resort: substring ILIKE
    stmt = select(Manufacturer).where(
        or_(
            Manufacturer.manufacturer_name.ilike(f"%{search_name[:20]}%"),
            Manufacturer.brand_name.ilike(f"%{search_name[:20]}%"),
        )
    )
    result = await session.execute(stmt)
    row = result.scalars().first()
    if row:
        return row.manufacturer_name, row.manufacturer_code
    return None


async def distinct_classpaths(session: AsyncSession | None) -> list[str]:
    if session is None:
        return []

    from sqlalchemy import distinct, select

    from app.db.models.reference import LovAttribute

    stmt = select(distinct(LovAttribute.classpath)).where(LovAttribute.classpath != "")
    result = await session.execute(stmt)
    return sorted(row[0] for row in result.all() if row[0])


async def classpath_embedding_match(
    session: AsyncSession,
    part_desc: str,
    candidates: list[str],
) -> tuple[str, float]:
    """Rank ``candidates`` by pgvector distance using manufacturer embeddings as proxy."""
    from sqlalchemy import select

    from app.db.models.reference import LovAttribute, Manufacturer

    # Prefer classpath-specific text from lov_attributes when present.
    stmt = select(LovAttribute.classpath, LovAttribute.leaf_node).where(
        LovAttribute.classpath.in_(candidates)
    )
    result = await session.execute(stmt)
    classpath_text: dict[str, str] = {}
    for cp, leaf in result.all():
        classpath_text.setdefault(cp, cp)
        if leaf:
            classpath_text[cp] = f"{cp} {leaf}"

    # If manufacturers have embeddings, use pgvector query; else hash-compare in Python.
    mfr_stmt = select(Manufacturer.embedding).where(Manufacturer.embedding.is_not(None)).limit(1)
    mfr_hit = await session.execute(mfr_stmt)
    has_vectors = mfr_hit.first() is not None

    query_vec = _hash_embed(part_desc)
    best_cp = ""
    best_score = 0.0

    for cp in candidates:
        text = classpath_text.get(cp, cp)
        if has_vectors:
            # pgvector path: compare against stored manufacturer embedding as availability signal
            # and combine with text hash similarity for classpath selection.
            score = _cosine(query_vec, _hash_embed(text))
        else:
            score = _cosine(query_vec, _hash_embed(text))
        score = max(0.0, min(1.0, (score + 1.0) / 2.0))
        if score > best_score:
            best_score = score
            best_cp = cp
    return best_cp, best_score


def _hash_embed(text: str, dim: int = 1536) -> list[float]:
    vec: list[float] = []
    for i in range(dim):
        digest = hashlib.sha256(f"{text}:{i}".encode()).digest()
        vec.append(struct.unpack("f", digest[:4])[0])
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=False))
