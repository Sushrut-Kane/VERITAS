"""Parse the messy ``Part_Manuf`` field into a manufacturer name + code."""
import re

_MFR_RE = re.compile(r"^\s*(?P<name>.*?)\s*\((?P<code>[^)]+)\)\s*$")


def parse_manufacturer(raw: str | None) -> tuple[str, str]:
    """``'Freud Inc (2435)'`` -> ``('Freud Inc', '2435')``.

    Returns ``(name, code)``; code is '' when there is no parenthesised code.
    """
    if not raw or not raw.strip():
        return "", ""
    match = _MFR_RE.match(raw)
    if match:
        return match.group("name").strip(), match.group("code").strip()
    return raw.strip(), ""
