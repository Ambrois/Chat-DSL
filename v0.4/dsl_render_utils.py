from __future__ import annotations

import html
import re
from functools import lru_cache
from typing import Any


_DEFAULT_SIGIL = "@"


def _normalize_sigil(sigil: object) -> str:
    if isinstance(sigil, str) and len(sigil) == 1:
        return sigil
    return _DEFAULT_SIGIL


@lru_cache(maxsize=None)
def _dsl_token_pattern(sigil: str) -> re.Pattern[str]:
    return re.compile(
        rf"(?<![A-Za-z0-9_])/(?:THEN|FROM|IN|DEF|TYPE|AS|OUT|IF|END)\b|(?<![A-Za-z0-9_]){re.escape(sigil)}[A-Za-z_][A-Za-z0-9_]*",
        flags=re.IGNORECASE,
    )


def dsl_to_highlighted_html(text: object, sigil: str = _DEFAULT_SIGIL) -> str:
    raw = text if isinstance(text, str) else str(text)
    pattern = _dsl_token_pattern(_normalize_sigil(sigil))
    parts: list[str] = []
    cursor = 0
    for match in pattern.finditer(raw):
        start, end = match.span()
        if start > cursor:
            parts.append(html.escape(raw[cursor:start]))
        token = match.group(0)
        css_class = "dsl-kw" if token.startswith("/") else "dsl-var"
        parts.append(f'<span class="{css_class}">{html.escape(token)}</span>')
        cursor = end
    if cursor < len(raw):
        parts.append(html.escape(raw[cursor:]))
    return "".join(parts)


def infer_message_sigil(message: Any, default: str = _DEFAULT_SIGIL) -> str:
    fallback = _normalize_sigil(default)
    if not isinstance(message, dict):
        return fallback

    meta = message.get("meta")
    if not isinstance(meta, dict):
        return fallback

    parsed_steps = meta.get("parsed_steps")
    if not isinstance(parsed_steps, list):
        return fallback

    for item in parsed_steps:
        if not isinstance(item, dict):
            continue
        sigil = item.get("sigil")
        if isinstance(sigil, str) and len(sigil) == 1:
            return sigil

    return fallback
