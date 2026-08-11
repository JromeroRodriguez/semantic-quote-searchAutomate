"""FastAPI application entry point.

Startup loads configuration, models, FAISS index and quote metadata once.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

from backend.app.api.routes.search import router as search_router
from backend.app.core.config import get_settings
from backend.app.core.logging import setup_logging
from backend.app.repositories.quote_repository import QuoteRepository
from backend.app.services.embeddings.jina_service import EmbeddingService
from backend.app.services.reranker.bge_service import BGERerankerService
from backend.app.services.search.faiss_service import FAISSService
from backend.app.services.search.semantic_search_service import SemanticSearchService

logger = logging.getLogger(__name__)


def _validate_resources() -> None:
    settings = get_settings()
    missing = []
    for label, path in (
        ("dataset", settings.quotes_path),
        ("FAISS index", settings.faiss_index_path),
        ("metadata", settings.metadata_path),
    ):
        if not path.exists():
            missing.append(f"{label} ({path})")
    if missing:
        raise RuntimeError(
            "Missing required resources: " + "; ".join(missing) + ". "
            "Run 'python scripts/scrape_quotes.py' and 'python scripts/build_index.py' first."
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("starting application")
    _validate_resources()

    settings = get_settings()
    repository = QuoteRepository(settings.quotes_path)
    embedding_service = EmbeddingService(
        settings.embedding_model, device=settings.device, dtype=settings.model_dtype
    )
    faiss_service = FAISSService(settings.faiss_index_path, settings.metadata_path)
    reranker_service = BGERerankerService(
        settings.reranker_model, device=settings.device, dtype=settings.model_dtype
    )
    search_service = SemanticSearchService(
        embedding_service=embedding_service,
        faiss_service=faiss_service,
        reranker_service=reranker_service,
        quote_repository=repository,
        top_k=settings.top_k,
        final_results=settings.final_results,
    )

    app.state.settings = settings
    app.state.search_service = search_service
    logger.info(
        "application ready (%s quotes in index, top_k=%s, final=%s)",
        faiss_service.size,
        settings.top_k,
        settings.final_results,
    )
    yield
    logger.info("application shutdown")


app = FastAPI(
    title="Semantic Quote Search Engine",
    description="Returns the 3 quotes most semantically relevant to a free-text "
    "description of a situation, emotion or thought.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(search_router, prefix="/api/v1")

# Mount static assets (JS, CSS)
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "src")), name="static")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse(str(FRONTEND_DIR / "index.html"))
