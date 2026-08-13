"""Tracks estimated token usage across all batches (pure Python)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BatchUsage:
    """Token usage for a single batch."""

    batch_id: int
    quote_ids: list[int] = field(default_factory=list)
    quotes: list[Any] = field(default_factory=list)
    quote_count: int = 0
    estimated_input_tokens: int = 0


@dataclass
class UsageReceipt:
    """Final aggregated usage report."""

    quotes_processed: int = 0
    batches_created: int = 0
    estimated_input_tokens: int = 0
    token_limit_per_request: int = 0


class UsageTracker:
    """Accumulates estimated token usage from batch processing and produces a receipt."""

    def __init__(self, token_limit_per_request: int) -> None:
        self._token_limit = token_limit_per_request
        self._batches: list[BatchUsage] = []
        self._total_estimated = 0
        self._total_quotes = 0

    def record_batch(
        self,
        batch_id: int,
        quote_ids: list[int],
        estimated_input_tokens: int,
        quotes: list[Any] | None = None,
    ) -> BatchUsage:
        """Record usage for a processed batch."""
        self._total_estimated += estimated_input_tokens
        self._total_quotes += len(quote_ids)

        usage = BatchUsage(
            batch_id=batch_id,
            quote_ids=quote_ids,
            quotes=quotes or [],
            quote_count=len(quote_ids),
            estimated_input_tokens=estimated_input_tokens,
        )
        self._batches.append(usage)
        return usage

    def get_receipt(self) -> UsageReceipt:
        """Generate the final aggregated usage receipt."""
        return UsageReceipt(
            quotes_processed=self._total_quotes,
            batches_created=len(self._batches),
            estimated_input_tokens=self._total_estimated,
            token_limit_per_request=self._token_limit,
        )

    def get_batch_usages(self) -> list[BatchUsage]:
        return list(self._batches)
