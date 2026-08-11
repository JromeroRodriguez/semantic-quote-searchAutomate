"""Data access for the quote dataset."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from backend.app.models.quote import Quote

logger = logging.getLogger(__name__)


class QuoteRepository:
    """Loads quotes from data/quotes.json and provides lookup by id."""

    def __init__(self, quotes_path: Path) -> None:
        self._quotes_path = quotes_path
        self._by_id: dict[int, Quote] = {}
        self._records: list[Quote] = []
        self._load()

    def _load(self) -> None:
        if not self._quotes_path.exists():
            raise FileNotFoundError(
                f"Dataset not found at {self._quotes_path}. "
                "Run 'python scripts/scrape_quotes.py' first."
            )
        with self._quotes_path.open("r", encoding="utf-8") as fh:
            try:
                raw = json.load(fh)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {self._quotes_path}: {exc}") from exc

        for item in raw:
            quote = Quote.from_dict(item)
            self._by_id[quote.id] = quote
            self._records.append(quote)
        logger.info("loaded %s quotes from %s", len(self._records), self._quotes_path)

    def get_by_id(self, quote_id: int) -> Quote | None:
        return self._by_id.get(quote_id)

    def get_many(self, quote_ids: list[int]) -> list[Quote]:
        return [q for qid in quote_ids if (q := self._by_id.get(qid)) is not None]

    def all(self) -> list[Quote]:
        return list(self._records)

    @property
    def count(self) -> int:
        return len(self._records)
