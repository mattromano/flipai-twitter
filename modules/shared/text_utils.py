"""Text utility helpers used across automation modules."""

from __future__ import annotations

from typing import Optional


def _normalize_text(value: Optional[str]) -> str:
    """Normalize text for placeholder detection."""
    if not value:
        return ""
    return value.lower().replace("\n", " ").strip()


def is_placeholder_twitter_text(text: Optional[str]) -> bool:
    """Return True when the provided twitter text looks like an unmet prompt template.

    The automation occasionally captures the instructional template instead of the
    generated bullets. This helper recognizes those placeholders so callers can
    retry extraction instead of posting invalid content.
    """
    normalized = _normalize_text(text)
    if not normalized:
        return False

    prompt_markers = (
        "concise bullet format",
        'format: "[topic]',
        "[topic]:",
        "[metric]",
        "html_chart",
        "this_concludes_the_analysis",
        "key fields:",
        "add a quick 260 character summary",
    )

    if any(marker in normalized for marker in prompt_markers):
        return True

    # Heuristic: lots of square brackets usually indicates placeholder tokens.
    bracket_count = normalized.count("[") + normalized.count("]")
    if bracket_count >= max(2, len(normalized) // 15):
        return True

    return False

