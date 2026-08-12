"""Tests for the usage tracker module."""

from backend.app.services.optimizer.usage_tracker import UsageTracker


class TestUsageTracker:
    def test_empty_tracker(self):
        tracker = UsageTracker(token_limit_per_request=1000)
        receipt = tracker.get_receipt()
        assert receipt.quotes_processed == 0
        assert receipt.batches_created == 0
        assert receipt.requests_completed == 0
        assert receipt.requests_failed == 0
        assert receipt.estimated_input_tokens == 0
        assert receipt.actual_input_tokens == 0
        assert receipt.actual_output_tokens == 0
        assert receipt.total_tokens == 0

    def test_single_batch_with_ollama_response(self):
        tracker = UsageTracker(token_limit_per_request=1000)
        tracker.record_batch(
            batch_id=1,
            quote_ids=[1, 2],
            estimated_input_tokens=500,
            ollama_response={"prompt_eval_count": 510, "eval_count": 200},
        )
        receipt = tracker.get_receipt()
        assert receipt.quotes_processed == 2
        assert receipt.batches_created == 1
        assert receipt.requests_completed == 1
        assert receipt.requests_failed == 0
        assert receipt.estimated_input_tokens == 500
        assert receipt.actual_input_tokens == 510
        assert receipt.actual_output_tokens == 200
        assert receipt.total_tokens == 710

    def test_single_batch_without_ollama_response(self):
        tracker = UsageTracker(token_limit_per_request=1000)
        tracker.record_batch(
            batch_id=1,
            quote_ids=[1],
            estimated_input_tokens=300,
            ollama_response=None,
        )
        receipt = tracker.get_receipt()
        assert receipt.requests_completed == 0
        assert receipt.requests_failed == 1
        assert receipt.estimated_input_tokens == 300
        assert receipt.actual_input_tokens == 0

    def test_multiple_batches_accumulate(self):
        tracker = UsageTracker(token_limit_per_request=1000)
        tracker.record_batch(
            batch_id=1, quote_ids=[1, 2], estimated_input_tokens=400,
            ollama_response={"prompt_eval_count": 410, "eval_count": 150},
        )
        tracker.record_batch(
            batch_id=2, quote_ids=[3], estimated_input_tokens=200,
            ollama_response={"prompt_eval_count": 210, "eval_count": 80},
        )
        receipt = tracker.get_receipt()
        assert receipt.quotes_processed == 3
        assert receipt.batches_created == 2
        assert receipt.requests_completed == 2
        assert receipt.estimated_input_tokens == 600
        assert receipt.actual_input_tokens == 620
        assert receipt.actual_output_tokens == 230
        assert receipt.total_tokens == 850

    def test_partial_failure(self):
        tracker = UsageTracker(token_limit_per_request=1000)
        tracker.record_batch(
            batch_id=1, quote_ids=[1], estimated_input_tokens=300,
            ollama_response={"prompt_eval_count": 310, "eval_count": 100},
        )
        tracker.record_batch(
            batch_id=2, quote_ids=[2], estimated_input_tokens=250,
            ollama_response=None,
        )
        receipt = tracker.get_receipt()
        assert receipt.requests_completed == 1
        assert receipt.requests_failed == 1
        assert receipt.estimated_input_tokens == 550
        assert receipt.actual_input_tokens == 310
        assert receipt.actual_output_tokens == 100
        assert receipt.total_tokens == 410

    def test_total_equals_input_plus_output(self):
        tracker = UsageTracker(token_limit_per_request=1000)
        tracker.record_batch(
            batch_id=1, quote_ids=[1], estimated_input_tokens=100,
            ollama_response={"prompt_eval_count": 100, "eval_count": 50},
        )
        tracker.record_batch(
            batch_id=2, quote_ids=[2], estimated_input_tokens=200,
            ollama_response={"prompt_eval_count": 200, "eval_count": 80},
        )
        receipt = tracker.get_receipt()
        assert receipt.total_tokens == receipt.actual_input_tokens + receipt.actual_output_tokens

    def test_get_batch_usages(self):
        tracker = UsageTracker(token_limit_per_request=1000)
        tracker.record_batch(
            batch_id=1, quote_ids=[1], estimated_input_tokens=100,
            ollama_response={"prompt_eval_count": 100, "eval_count": 50},
        )
        usages = tracker.get_batch_usages()
        assert len(usages) == 1
        assert usages[0].batch_id == 1
        assert usages[0].estimated_input_tokens == 100
        assert usages[0].actual_input_tokens == 100
        assert usages[0].actual_output_tokens == 50
        assert usages[0].total_tokens == 150

    def test_ollama_response_without_eval_fields(self):
        tracker = UsageTracker(token_limit_per_request=1000)
        tracker.record_batch(
            batch_id=1, quote_ids=[1], estimated_input_tokens=100,
            ollama_response={"response": "some text"},
        )
        receipt = tracker.get_receipt()
        assert receipt.actual_input_tokens == 0
        assert receipt.actual_output_tokens == 0
        assert receipt.total_tokens == 0
