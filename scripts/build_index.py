"""Build the FAISS index from the scraped quote dataset.

Reads data/quotes.json, generates Jina embeddings (task: retrieval.passage),
builds a normalized cosine-similarity FAISS index and persists it together
with metadata that maps index rows back to quotes.

Outputs:
    data/quotes.index
    data/metadata.json

This is a data preparation process. It is never executed during a user search.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import faiss

from backend.app.core.config import get_settings
from backend.app.services.embeddings.jina_service import EmbeddingService
from backend.app.utils.text import clean_text, normalize_for_embedding

logger = logging.getLogger("build_index")


def load_quotes(quotes_path: Path) -> list[dict]:
    """Load and validate quote records from the dataset JSON."""
    if not quotes_path.exists():
        raise FileNotFoundError(f"Dataset not found at {quotes_path}. Run scrape_quotes.py first.")
    with quotes_path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)

    quotes: list[dict] = []
    for record in raw:
        if not record.get("id") or not record.get("author") or not record.get("quote"):
            logger.warning("skipping invalid record: %s", record)
            continue
        quotes.append(record)
    return quotes


def deduplicate_quotes(quotes: list[dict]) -> list[dict]:
    """Deduplicate by normalized quote text, preserving the first record."""
    seen: set[str] = set()
    unique: list[dict] = []
    for record in quotes:
        key = normalize_for_embedding(record["quote"])
        if key in seen:
            logger.info("duplicate dropped (id=%s): %s", record["id"], record["quote"][:60])
            continue
        seen.add(key)
        unique.append(record)
    return unique


def build_index(
    quotes_path: Path,
    index_path: Path,
    metadata_path: Path,
    model_name: str,
    device: str | None,
    dtype: str,
    batch_size: int,
) -> None:
    """Generate embeddings and persist the FAISS index + metadata."""
    quotes = load_quotes(quotes_path)
    quotes = deduplicate_quotes(quotes)
    logger.info("indexing %s quotes", len(quotes))

    texts = [clean_text(q["quote"]) for q in quotes]

    embedding_service = EmbeddingService(model_name, device=device, dtype=dtype)
    t0 = time.perf_counter()
    embeddings = embedding_service.embed_passages(texts, batch_size=batch_size)
    logger.info("embedded %s passages in %.2fs", len(texts), time.perf_counter() - t0)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype("float32"))

    index_path.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(index_path))

    metadata = [{"quote_id": q["id"], "quote": q["quote"], "author": q["author"]} for q in quotes]
    with metadata_path.open("w", encoding="utf-8") as fh:
        json.dump(metadata, fh, ensure_ascii=False, indent=2)

    logger.info("FAISS index written to %s (%s vectors, dim=%s)", index_path, index.ntotal, dim)
    logger.info("metadata written to %s", metadata_path)


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def main(argv: list[str] | None = None) -> int:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Build the FAISS semantic index")
    parser.add_argument("-q", "--quotes-path", default=str(settings.quotes_path))
    parser.add_argument("-i", "--index-path", default=str(settings.faiss_index_path))
    parser.add_argument("-m", "--metadata-path", default=str(settings.metadata_path))
    parser.add_argument("--model", default=settings.embedding_model)
    parser.add_argument("--device", default=settings.device)
    parser.add_argument("--dtype", default=settings.model_dtype)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    setup_logging(args.verbose)
    try:
        build_index(
            quotes_path=Path(args.quotes_path),
            index_path=Path(args.index_path),
            metadata_path=Path(args.metadata_path),
            model_name=args.model,
            device=args.device,
            dtype=args.dtype,
            batch_size=args.batch_size,
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("index build failed: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
