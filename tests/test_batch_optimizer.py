"""Tests for the batch optimizer module."""

import pytest

from backend.app.services.optimizer.batch_optimizer import BatchOptimizer, QuoteRecord
from backend.app.services.optimizer.prompt_builder import build_prompt
from backend.app.services.optimizer.tokenizer import Tokenizer


def _make_quote(id: int, text: str = None) -> QuoteRecord:
    if text is None:
        text = f"This is quote number {id} with some sample text."
    return QuoteRecord(id=id, quote=text, author=f"Author {id}")


def _make_optimizer(max_tokens: int) -> BatchOptimizer:
    tokenizer = Tokenizer()
    return BatchOptimizer(
        max_tokens_per_request=max_tokens,
        prompt_builder=build_prompt,
        tokenizer_count=tokenizer.count,
    )


class TestBatchOptimizer:
    def test_empty_dataset(self):
        opt = _make_optimizer(1000)
        batches = opt.pack([])
        assert batches == []

    def test_single_quote_fits(self):
        opt = _make_optimizer(1000)
        quotes = [_make_quote(1)]
        batches = opt.pack(quotes)
        assert len(batches) == 1
        assert batches[0].quote_count == 1
        assert batches[0].prompt_tokens > 0
        assert batches[0].prompt_tokens <= 1000

    def test_two_quotes_fit(self):
        opt = _make_optimizer(1000)
        quotes = [_make_quote(1, "Short quote."), _make_quote(2, "Another short quote.")]
        batches = opt.pack(quotes)
        assert len(batches) == 1
        assert batches[0].quote_count == 2

    def test_quotes_exceed_limit_creates_new_batch(self):
        long_text = "This is a very long quote with many words. " * 10
        opt = _make_optimizer(200)
        quotes = [_make_quote(1, long_text), _make_quote(2, long_text)]
        batches = opt.pack(quotes)
        assert len(batches) == 2

    def test_many_quotes_packed_correctly(self):
        opt = _make_optimizer(1000)
        quotes = [_make_quote(i, f"Quote {i}: short text.") for i in range(1, 20)]
        batches = opt.pack(quotes)
        assert len(batches) >= 1
        all_ids = []
        for b in batches:
            all_ids.extend(b.quote_ids)
            assert b.prompt_tokens <= 1000
        assert all_ids == list(range(1, 20))

    def test_preserves_quote_order(self):
        opt = _make_optimizer(1000)
        quotes = [_make_quote(i) for i in range(1, 11)]
        batches = opt.pack(quotes)
        all_ids = []
        for b in batches:
            all_ids.extend(b.quote_ids)
        assert all_ids == list(range(1, 11))

    def test_oversized_single_quote(self):
        huge_text = "word " * 500
        opt = _make_optimizer(100)
        quotes = [_make_quote(1, huge_text)]
        batches = opt.pack(quotes)
        assert len(batches) == 1
        assert batches[0].prompt_tokens > 100

    def test_prompt_tokens_never_exceed_limit(self):
        opt = _make_optimizer(500)
        quotes = [_make_quote(i, f"Quote {i} with enough text to fill space. " * 3) for i in range(1, 30)]
        batches = opt.pack(quotes)
        for b in batches:
            assert b.prompt_tokens <= 500

    def test_every_batch_has_prompt_tokens(self):
        opt = _make_optimizer(1000)
        quotes = [_make_quote(i) for i in range(1, 6)]
        batches = opt.pack(quotes)
        for b in batches:
            assert b.prompt_tokens > 0

    def test_invalid_max_tokens_raises(self):
        tokenizer = Tokenizer()
        with pytest.raises(ValueError):
            BatchOptimizer(
                max_tokens_per_request=0,
                prompt_builder=build_prompt,
                tokenizer_count=tokenizer.count,
            )

    def test_negative_max_tokens_raises(self):
        tokenizer = Tokenizer()
        with pytest.raises(ValueError):
            BatchOptimizer(
                max_tokens_per_request=-10,
                prompt_builder=build_prompt,
                tokenizer_count=tokenizer.count,
            )


class TestPromptBuilder:
    def test_build_prompt_with_quotes(self):
        quotes = [_make_quote(1, "Test quote.")]
        prompt = build_prompt(quotes)
        assert "Test quote." in prompt
        assert "Author 1" in prompt

    def test_build_prompt_empty(self):
        prompt = build_prompt([])
        assert prompt == ""

    def test_build_prompt_ordering(self):
        quotes = [_make_quote(1, "First."), _make_quote(2, "Second.")]
        prompt = build_prompt(quotes)
        pos1 = prompt.index("First.")
        pos2 = prompt.index("Second.")
        assert pos1 < pos2

    def test_build_prompt_format(self):
        quotes = [_make_quote(1, "Quote A."), _make_quote(2, "Quote B.")]
        prompt = build_prompt(quotes)
        assert '"Quote A." — Author 1' in prompt
        assert '"Quote B." — Author 2' in prompt
