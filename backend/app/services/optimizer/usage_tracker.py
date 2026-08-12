"""Tracks estimated and actual token usage across all batches.

 Accumulates per-batch metrics and produces a final usage receipt.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BatchUsage:
    """Token usage for a single batch."""

    batch_id: int
    quote_ids: list[int] = field(default_factory=list)
    quote_count: int = 0
    estimated_input_tokens: int = 0
    actual_input_tokens: int | None = None
    actual_output_tokens: int | None = None
    total_tokens: int | None = None


@dataclass
class UsageReceipt:
    """Final aggregated usage report."""

    quotes_processed: int = 0
    batches_created: int = 0
    requests_completed: int = 0
    requests_failed: int = 0
    estimated_input_tokens: int = 0
    actual_input_tokens: int = 0
    actual_output_tokens: int = 0
    total_tokens: int = 0
    token_limit_per_request: int = 0


class UsageTracker:
    """Accumulates token usage from batch processing and produces a receipt."""

    def __init__(self, token_limit_per_request: int) -> None:
        self._token_limit = token_limit_per_request
        self._batches: list[BatchUsage] = []
        self._total_estimated = 0
        self._total_actual_input = 0
        self._total_actual_output = 0
        self._total_actual = 0
        self._requests_completed = 0
        self._requests_failed = 0
        self._total_quotes = 0

    def record_batch(
        self,
        batch_id: int,
        quote_ids: list[int],
        estimated_input_tokens: int,
        ollama_response: dict[str, Any] | None = None,
        skipped: bool = False,
    ) -> BatchUsage:
        """Record usage for a processed batch.

        If skipped=True (LLM processing disabled), no success/failure is counted.
        If ollama_response is None and skipped=False, the request failed.
        """
        actual_input = None
        actual_output = None
        actual_total = None

        if skipped:
            pass
        elif ollama_response is not None:
            # Ollama returns prompt_eval_count, eval_count, prompt_eval_duration, eval_duration
            actual_input = ollama_response.get("prompt_eval_count")
            actual_output = ollama_response.get("eval_count")
            if actual_input is not None and actual_output is not None:
                actual_total = actual_input + actual_output

            self._total_actual_input += actual_input or 0
            self._total_actual_output += actual_output or 0
            self._total_actual += actual_total or 0
            self._requests_completed += 1
        else:
            self._requests_failed += 1

        self._total_estimated += estimated_input_tokens
        self._total_quotes += len(quote_ids)

        usage = BatchUsage(
            batch_id=batch_id,
            quote_ids=quote_ids,
            quote_count=len(quote_ids),
            estimated_input_tokens=estimated_input_tokens,
            actual_input_tokens=actual_input,
            actual_output_tokens=actual_output,
            total_tokens=actual_total,
        )
        self._batches.append(usage)
        return usage

    def get_receipt(self) -> UsageReceipt:
        """Generate the final aggregated usage receipt."""
        return UsageReceipt(
            quotes_processed=self._total_quotes,
            batches_created=len(self._batches),
            requests_completed=self._requests_completed,
            requests_failed=self._requests_failed,
            estimated_input_tokens=self._total_estimated,
            actual_input_tokens=self._total_actual_input,
            actual_output_tokens=self._total_actual_output,
            total_tokens=self._total_actual,
            token_limit_per_request=self._token_limit,
        )

    def get_batch_usages(self) -> list[BatchUsage]:
        return list(self._batches)
