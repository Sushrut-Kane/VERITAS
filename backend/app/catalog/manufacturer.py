"""Parse the messy ``Part_Manuf`` field into a manufacturer name + code."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

_MFR_RE = re.compile(r"^\s*(?P<name>.*?)\s*\((?P<code>[^)]+)\)\s*$")


def _regex_parse(raw: str | None) -> tuple[str, str]:
    if not raw or not raw.strip():
        return "", ""
    match = _MFR_RE.match(raw)
    if match:
        return match.group("name").strip(), match.group("code").strip()
    return raw.strip(), ""


def parse_manufacturer(
    raw: str | None, *, session: AsyncSession | None = None
) -> tuple[str, str]:
    """``'Freud Inc (2435)'`` -> ``('Freud Inc', '2435')``.

    Returns ``(name, code)``; code is '' when there is no parenthesised code.
    When ``session`` is provided, use :func:`parse_manufacturer_async` from async
    code — this sync entry point keeps regex-only behaviour so stateless callers
    and unit tests stay unchanged.
    """
    del session  # DB lookup requires the async helper below.
    return _regex_parse(raw)


async def parse_manufacturer_async(
    raw: str | None, *, session: AsyncSession | None = None
) -> tuple[str, str]:
    """Async variant: manufacturers-table lookup (exact then fuzzy) before regex."""
    if session is not None and raw and raw.strip():
        from app.catalog.reference_lookup import lookup_manufacturer

        hit = await lookup_manufacturer(session, raw)
        if hit:
            return hit
    return _regex_parse(raw)
