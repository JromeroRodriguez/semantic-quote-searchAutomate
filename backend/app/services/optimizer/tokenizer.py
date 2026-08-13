"""Token counting using OpenAI's tiktoken library."""

from __future__ import annotations

import logging
from functools import lru_cache

import tiktoken

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _load_tokenizer():
    logger.info("loading OpenAI tiktoken encoder (cl100k_base)")
    encoding = tiktoken.get_encoding("cl100k_base")
    logger.info("OpenAI tokenizer ready")
    return encoding


class Tokenizer:
    """Counts tokens using OpenAI's tiktoken."""

    def count(self, text: str) -> int:
        """Return the number of tokens in the given text."""
        if not text:
            return 0
        encoding = _load_tokenizer()
        return len(encoding.encode(text))

    def count_batch(self, texts: list[str]) -> list[int]:
        """Return token counts for a list of texts."""
        return [self.count(t) for t in texts]
