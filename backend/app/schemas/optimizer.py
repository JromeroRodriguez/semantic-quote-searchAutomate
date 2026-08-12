"""Pydantic schemas for the budget optimizer API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class OptimizerRequest(BaseModel):
    max_tokens: int = Field(gt=0, description="Maximum token budget per batch")


class BatchResult(BaseModel):
    batch_id: int
    quote_ids: list[int]
    quote_count: int
    estimated_input_tokens: int
    actual_input_tokens: int | None = None
    actual_output_tokens: int | None = None
    total_tokens: int | None = None


class UsageReceipt(BaseModel):
    quotes_processed: int
    batches_created: int
    requests_completed: int
    requests_failed: int
    estimated_input_tokens: int
    actual_input_tokens: int
    actual_output_tokens: int
    total_tokens: int
    token_limit_per_request: int


class OptimizerResponse(BaseModel):
    success: bool
    receipt: UsageReceipt
    batches: list[BatchResult]
