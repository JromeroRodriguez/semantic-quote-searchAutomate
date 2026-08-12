"""Token counting using the Qwen2.5 tokenizer via Hugging Face transformers.

Provides accurate token counting compatible with the local Ollama model.
Isolated behind a clean interface so it can be replaced without affecting batching logic.
"""

from __future__ import annotations

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

QWEN_MODEL_NAME = "Qwen/Qwen2.5-0.5B"


@lru_cache(maxsize=1)
def _load_tokenizer():
    from transformers import AutoTokenizer

    logger.info("loading tokenizer %s", QWEN_MODEL_NAME)
    tokenizer = AutoTokenizer.from_pretrained(QWEN_MODEL_NAME)
    logger.info("tokenizer ready")
    return tokenizer


class Tokenizer:
    """Counts tokens using the Qwen2.5 tokenizer."""

    def count(self, text: str) -> int:
        """Return the number of tokens in the given text."""
        if not text:
            return 0
        tokenizer = _load_tokenizer()
        return len(tokenizer.encode(text))

    def count_batch(self, texts: list[str]) -> list[int]:
        """Return token counts for a list of texts."""
        return [self.count(t) for t in texts]
