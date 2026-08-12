"""Prompt construction for the optimizer pipeline.

 Builds the text representation whose token count is measured for batching.
 Includes quote text and author names — the actual content to be tokenized.
"""

from __future__ import annotations

from backend.app.services.optimizer.batch_optimizer import QuoteRecord


def build_prompt(quotes: list[QuoteRecord]) -> str:
    """Build the text representation of a batch of quotes.

    This is the text whose token count determines whether a batch fits
    within the configured limit. Includes quote text and author attribution.
    """
    if not quotes:
        return ""

    return "\n".join(
        f'"{q.quote}" — {q.author}'
        for q in quotes
    )
