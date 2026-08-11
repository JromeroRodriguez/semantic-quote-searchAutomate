"""Text normalization utilities shared across the project."""

from __future__ import annotations

import re

CURLY_QUOTES = {"\u201c", "\u201d", "\u2018", "\u2019"}
WHITESPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """Remove typographic quotes and normalize whitespace.

    Preserves the original display text as much as possible while
    producing a stable key for deduplication.
    """
    cleaned = text.strip()
    for quote in CURLY_QUOTES:
        cleaned = cleaned.replace(quote, "")
    cleaned = WHITESPACE_RE.sub(" ", cleaned).strip()
    return cleaned


def normalize_for_embedding(text: str) -> str:
    """Normalize a quote for embedding input."""
    return clean_text(text).strip().lower()
