"""Pydantic schemas for the budget optimizer API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class OptimizerRequest(BaseModel):
    max_tokens: int = Field(gt=0, description="Maximum token budget per batch")


class QuoteSummary(BaseModel):
    id: int
    quote: str
    author: str


class BatchResult(BaseModel):
    batch_id: int
    quote_ids: list[int]
    quotes: list[QuoteSummary] = []
    quote_count: int
    estimated_input_tokens: int


class UsageReceipt(BaseModel):
    quotes_processed: int
    batches_created: int
    estimated_input_tokens: int
    token_limit_per_request: int


class OptimizerResponse(BaseModel):
    success: bool
    receipt: UsageReceipt
    batches: list[BatchResult]
