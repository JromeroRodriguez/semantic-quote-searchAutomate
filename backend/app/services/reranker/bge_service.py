"""BGE reranker wrapper using a CrossEncoder."""

from __future__ import annotations

import logging
from typing import Any

import torch

logger = logging.getLogger(__name__)


class BGERerankerService:
    """Ranks candidates using BAAI/bge-reranker-v2-m3."""

    def __init__(
        self,
        model_name: str,
        device: str | None = None,
        dtype: str = "float32",
    ) -> None:
        self._device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        from sentence_transformers import CrossEncoder

        logger.info("loading reranker %s on %s", model_name, self._device)
        self._model = CrossEncoder(
            model_name,
            device=self._device,
            trust_remote_code=True,
        )
        logger.info("reranker ready")

    def rerank(self, query: str, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Return candidates sorted by relevance to the query (descending)."""
        if not candidates:
            return []

        pairs = [(query, candidate["quote"]) for candidate in candidates]
        scores = self._model.predict(pairs, batch_size=8, convert_to_numpy=True)

        scored = sorted(zip(candidates, scores), key=lambda item: item[1], reverse=True)
        return [candidate for candidate, _score in scored]
