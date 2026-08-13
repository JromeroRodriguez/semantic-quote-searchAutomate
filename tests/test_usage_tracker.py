"""Tests for the usage tracker module (pure Python estimation)."""

from backend.app.services.optimizer.usage_tracker import UsageTracker


class TestUsageTracker:
    def test_empty_tracker(self):
        tracker = UsageTracker(token_limit_per_request=1000)
        receipt = tracker.get_receipt()
        assert receipt.quotes_processed == 0
        assert receipt.batches_created == 0
        assert receipt.estimated_input_tokens == 0
        assert receipt.token_limit_per_request == 1000

    def test_single_batch(self):
        tracker = UsageTracker(token_limit_per_request=1000)
        tracker.record_batch(
            batch_id=1,
            quote_ids=[1, 2],
            estimated_input_tokens=500,
        )
        receipt = tracker.get_receipt()
        assert receipt.quotes_processed == 2
        assert receipt.batches_created == 1
        assert receipt.estimated_input_tokens == 500

    def test_multiple_batches_accumulate(self):
        tracker = UsageTracker(token_limit_per_request=1000)
        tracker.record_batch(
            batch_id=1, quote_ids=[1, 2], estimated_input_tokens=400,
        )
        tracker.record_batch(
            batch_id=2, quote_ids=[3], estimated_input_tokens=200,
        )
        receipt = tracker.get_receipt()
        assert receipt.quotes_processed == 3
        assert receipt.batches_created == 2
        assert receipt.estimated_input_tokens == 600

    def test_get_batch_usages(self):
        tracker = UsageTracker(token_limit_per_request=1000)
        tracker.record_batch(
            batch_id=1, quote_ids=[1], estimated_input_tokens=100,
        )
        usages = tracker.get_batch_usages()
        assert len(usages) == 1
        assert usages[0].batch_id == 1
        assert usages[0].estimated_input_tokens == 100
