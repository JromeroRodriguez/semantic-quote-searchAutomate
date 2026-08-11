"""Orchestration of the semantic search pipeline.

Pipeline: query embedding -> FAISS candidate retrieval -> BGE reranking -> top K.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from backend.app.repositories.quote_repository import QuoteRepository
from backend.app.services.embeddings.jina_service import EmbeddingService
from backend.app.services.reranker.bge_service import BGERerankerService
from backend.app.services.search.faiss_service import FAISSService

logger = logging.getLogger(__name__)


class SemanticSearchService:
    """Coordinates the full search pipeline."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        faiss_service: FAISSService,
        reranker_service: BGERerankerService,
        quote_repository: QuoteRepository,
        top_k: int,
        final_results: int,
    ) -> None:
        self._embedding = embedding_service
        self._faiss = faiss_service
        self._reranker = reranker_service
        self._repository = quote_repository
        self._top_k = top_k
        self._final_results = final_results

    def search(self, query: str) -> list[dict[str, Any]]:
        t0 = time.perf_counter()

        query_embedding = self._embedding.embed_query(query)
        t1 = time.perf_counter()

        candidates = self._faiss.search(query_embedding, self._top_k)
        t2 = time.perf_counter()

        resolved = [
            {
                "quote_id": c["quote_id"],
                "quote": quote.quote,
                "author": quote.author,
            }
            for c in candidates
            if (quote := self._repository.get_by_id(c["quote_id"])) is not None
        ]

        ranked = self._reranker.rerank(query, resolved)
        t3 = time.perf_counter()

        logger.info(
            "[PERF] embedding: %.4fs faiss: %.4fs reranker: %.4fs total: %.4fs "
            "(candidates=%s, final=%s)",
            t1 - t0,
            t2 - t1,
            t3 - t2,
            t3 - t0,
            len(candidates),
            min(len(ranked), self._final_results),
        )

        return ranked[: self._final_results]
