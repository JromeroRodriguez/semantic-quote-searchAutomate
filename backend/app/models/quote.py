"""Domain model for a quote."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class Quote(BaseModel):
    """A single quote as stored in quotes.json."""

    id: int
    author: str
    quote: str
    source: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Quote:
        return cls.model_validate(data)
