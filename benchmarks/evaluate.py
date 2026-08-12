"""Evaluate semantic search quality against the benchmark queries."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def run_benchmark():
    from backend.app.core.config import get_settings
    from backend.app.core.logging import setup_logging
    from backend.app.repositories.quote_repository import QuoteRepository
    from backend.app.services.embeddings.jina_service import EmbeddingService
    from backend.app.services.reranker.bge_service import BGERerankerService
    from backend.app.services.search.faiss_service import FAISSService
    from backend.app.services.search.semantic_search_service import (
        SemanticSearchService,
    )

    setup_logging()
    settings = get_settings()
    repository = QuoteRepository(settings.quotes_path)
    embedding = EmbeddingService(
        settings.embedding_model, device=settings.device, dtype=settings.model_dtype
    )
    faiss = FAISSService(settings.faiss_index_path, settings.metadata_path)
    reranker = BGERerankerService(
        settings.reranker_model, device=settings.device, dtype=settings.model_dtype
    )
    search = SemanticSearchService(embedding, faiss, reranker, repository, settings.top_k, settings.final_results)

    queries_path = PROJECT_ROOT / "benchmarks" / "queries.json"
    with queries_path.open("r", encoding="utf-8") as fh:
        queries = json.load(fh)

    print(f"\n{'='*70}")
    print(f"{'Type':<25} {'Query':<50} {'Top 1 Quote'}")
    print(f"{'='*70}")

    total_latency = 0.0
    for q in queries:
        t0 = time.perf_counter()
        results = search.search(q["query"])
        latency = time.perf_counter() - t0
        total_latency += latency

        top = results[0]["quote"][:70] if results else "NO RESULTS"
        print(f"{q['type']:<25} {q['query'][:50]:<50} {top}")

    avg = total_latency / len(queries)
    print(f"\n{'='*70}")
    print(f"Total queries: {len(queries)}")
    print(f"Total latency: {total_latency:.2f}s")
    print(f"Average latency: {avg:.2f}s")
    print(f"{'='*70}")


if __name__ == "__main__":
    run_benchmark()
