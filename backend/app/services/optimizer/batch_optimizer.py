"""Greedy batch packing algorithm using actual tokenization.

 Builds the text representation for each candidate batch and tokenizes it
 to ensure the total tokens never exceed the configured limit.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable

logger = logging.getLogger(__name__)


@dataclass
class QuoteRecord:
    """A validated quote."""

    id: int
    quote: str
    author: str
    source: str = ""


@dataclass
class Batch:
    """A packed batch of quotes with its estimated token count."""

    batch_id: int
    quotes: list[QuoteRecord] = field(default_factory=list)
    prompt_tokens: int = 0

    @property
    def quote_ids(self) -> list[int]:
        return [q.id for q in self.quotes]

    @property
    def quote_count(self) -> int:
        return len(self.quotes)


class BatchOptimizer:
    """Packs quotes into batches by building the actual text and checking
    its token count against the limit.

    Uses a greedy first-fit algorithm:
      1. Start with an empty batch.
      2. For each quote, build the candidate text (current batch + quote).
      3. Tokenize the candidate text.
      4. If tokens <= max_tokens, add the quote.
      5. If tokens > max_tokens, close the batch and start a new one.
    """

    def __init__(
        self,
        max_tokens_per_request: int,
        prompt_builder: Callable[[list[QuoteRecord]], str],
        tokenizer_count: Callable[[str], int],
    ) -> None:
        if max_tokens_per_request <= 0:
            raise ValueError("max_tokens_per_request must be positive")

        self._max_tokens = max_tokens_per_request
        self._build_prompt = prompt_builder
        self._count_tokens = tokenizer_count

    @property
    def max_tokens(self) -> int:
        return self._max_tokens

    def _estimate_tokens(self, quotes: list[QuoteRecord]) -> int:
        """Build the text and count its tokens."""
        text = self._build_prompt(quotes)
        return self._count_tokens(text)

    def pack(self, quotes: list[QuoteRecord]) -> list[Batch]:
        """Pack quotes into batches respecting the token budget.

        Algorithm:
          1. Walk quotes in order.
          2. For each quote, build candidate text with current batch + quote.
          3. Tokenize the candidate text.
          4. If <= max_tokens, add quote to current batch.
          5. If > max_tokens, close current batch, start new one with this quote.
          6. If a single quote alone exceeds max_tokens, place it in its own
             batch with a warning (oversized).
        """
        if not quotes:
            return []

        batches: list[Batch] = []
        current_quotes: list[QuoteRecord] = []
        current_tokens = 0

        for quote in quotes:
            candidate = current_quotes + [quote]
            candidate_tokens = self._estimate_tokens(candidate)

            if not current_quotes:
                if candidate_tokens > self._max_tokens:
                    oversized = Batch(
                        batch_id=len(batches) + 1,
                        quotes=[quote],
                        prompt_tokens=candidate_tokens,
                    )
                    batches.append(oversized)
                    logger.warning(
                        "quote %d produces %d tokens (limit=%d) — oversized",
                        quote.id,
                        candidate_tokens,
                        self._max_tokens,
                    )
                    continue
                current_quotes = [quote]
                current_tokens = candidate_tokens
            else:
                if candidate_tokens <= self._max_tokens:
                    current_quotes.append(quote)
                    current_tokens = candidate_tokens
                else:
                    batches.append(Batch(
                        batch_id=len(batches) + 1,
                        quotes=list(current_quotes),
                        prompt_tokens=current_tokens,
                    ))
                    single_tokens = self._estimate_tokens([quote])
                    if single_tokens > self._max_tokens:
                        oversized = Batch(
                            batch_id=len(batches) + 1,
                            quotes=[quote],
                            prompt_tokens=single_tokens,
                        )
                        batches.append(oversized)
                        logger.warning(
                            "quote %d produces %d tokens (limit=%d) — oversized",
                            quote.id,
                            single_tokens,
                            self._max_tokens,
                        )
                        current_quotes = []
                        current_tokens = 0
                    else:
                        current_quotes = [quote]
                        current_tokens = single_tokens

        if current_quotes:
            batches.append(Batch(
                batch_id=len(batches) + 1,
                quotes=list(current_quotes),
                prompt_tokens=current_tokens,
            ))

        return batches
