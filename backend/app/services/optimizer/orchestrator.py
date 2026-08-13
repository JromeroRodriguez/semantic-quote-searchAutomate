"""Orchestrates the complete budget optimizer workflow (pure Python)."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from backend.app.services.optimizer.batch_optimizer import BatchOptimizer, QuoteRecord
from backend.app.services.optimizer.prompt_builder import build_prompt
from backend.app.services.optimizer.tokenizer import Tokenizer
from backend.app.services.optimizer.usage_tracker import UsageTracker

logger = logging.getLogger(__name__)


def _load_quotes(quotes_path: Path) -> list[dict[str, Any]]:
    """Load and validate quotes from the JSON dataset."""
    if not quotes_path.exists():
        raise FileNotFoundError(f"Dataset not found at {quotes_path}")
    with quotes_path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)
    if not isinstance(raw, list):
        raise ValueError("Dataset must be a JSON array")
    return raw


def _validate_quote(record: dict[str, Any], index: int) -> QuoteRecord | None:
    """Validate a single quote record. Returns None if invalid."""
    quote_id = record.get("id")
    quote_text = record.get("quote", "").strip()
    author = record.get("author", "").strip()
    source = record.get("source", "")

    if not quote_id or not isinstance(quote_id, int):
        logger.warning("skipping record %d: missing or invalid id", index)
        return None
    if not quote_text:
        logger.warning("skipping record %d (id=%s): empty quote text", index, quote_id)
        return None
    if not author:
        logger.warning("skipping record %d (id=%s): empty author", index, quote_id)
        return None

    return QuoteRecord(
        id=quote_id,
        quote=quote_text,
        author=author,
        source=source,
    )


def run_optimizer(
    quotes_path: Path,
    max_tokens: int,
) -> dict[str, Any]:
    """Execute the pure Python optimizer pipeline.

    Args:
        quotes_path: Path to quotes.json
        max_tokens: Maximum tokens per batch

    Returns a dict with:
      - success: bool
      - receipt: usage summary
      - batches: list of batch summaries
    """
    # 1. Load quotes
    raw_quotes = _load_quotes(quotes_path)
    if not raw_quotes:
        return _empty_result(max_tokens)

    # 2. Validate quotes
    quotes: list[QuoteRecord] = []
    for i, record in enumerate(raw_quotes):
        qr = _validate_quote(record, i)
        if qr is not None:
            quotes.append(qr)

    if not quotes:
        return _empty_result(max_tokens)

    logger.info("validated %d quotes", len(quotes))

    # 3. Create batches using OpenAI tokenizer
    tokenizer = Tokenizer()
    optimizer = BatchOptimizer(
        max_tokens_per_request=max_tokens,
        prompt_builder=build_prompt,
        tokenizer_count=tokenizer.count,
    )
    batches = optimizer.pack(quotes)
    logger.info("created %d batches for %d quotes (limit=%d)", len(batches), len(quotes), max_tokens)

    # 4. Track usage (pure Python estimation)
    tracker = UsageTracker(token_limit_per_request=max_tokens)

    for batch in batches:
        batch_quotes_data = [{"id": q.id, "quote": q.quote, "author": q.author} for q in batch.quotes]
        tracker.record_batch(
            batch_id=batch.batch_id,
            quote_ids=batch.quote_ids,
            estimated_input_tokens=batch.prompt_tokens,
            quotes=batch_quotes_data,
        )

    receipt = tracker.get_receipt()
    batch_usages = tracker.get_batch_usages()

    return {
        "success": True,
        "receipt": {
            "quotes_processed": receipt.quotes_processed,
            "batches_created": receipt.batches_created,
            "estimated_input_tokens": receipt.estimated_input_tokens,
            "token_limit_per_request": receipt.token_limit_per_request,
        },
        "batches": [
            {
                "batch_id": bu.batch_id,
                "quote_ids": bu.quote_ids,
                "quotes": bu.quotes,
                "quote_count": bu.quote_count,
                "estimated_input_tokens": bu.estimated_input_tokens,
            }
            for bu in batch_usages
        ],
    }


def _empty_result(max_tokens: int) -> dict[str, Any]:
    return {
        "success": True,
        "receipt": {
            "quotes_processed": 0,
            "batches_created": 0,
            "estimated_input_tokens": 0,
            "token_limit_per_request": max_tokens,
        },
        "batches": [],
    }
