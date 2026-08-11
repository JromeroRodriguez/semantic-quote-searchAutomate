"""Pydantic schemas for the debate feature."""

from __future__ import annotations

from pydantic import BaseModel, Field

from backend.app.schemas.search import QuoteResult


class DebateRequest(BaseModel):
    query: str = Field(min_length=1, description="Philosophical or complex question to debate")


class DebateResponse(BaseModel):
    success: bool
    essay: str
    sources: list[QuoteResult]
