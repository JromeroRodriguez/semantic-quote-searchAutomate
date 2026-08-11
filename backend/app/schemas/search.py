"""Pydantic schemas for the search API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, description="Free-text description of a situation, emotion or thought")


class QuoteResult(BaseModel):
    id: int
    quote: str
    author: str


class SearchResponse(BaseModel):
    results: list[QuoteResult]


class ErrorResponse(BaseModel):
    detail: str
