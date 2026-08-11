"""Tests for FAISS index operations."""

from __future__ import annotations

import numpy as np
import pytest

from backend.app.services.search.faiss_service import FAISSService


@pytest.fixture(scope="module")
def faiss_service():
    from pathlib import Path
    project = Path(__file__).resolve().parents[1]
    return FAISSService(project / "data" / "quotes.index", project / "data" / "metadata.json")


def test_index_loaded(faiss_service):
    assert faiss_service.size == 100


def test_search_returns_results(faiss_service):
    vector = np.random.randn(384).astype("float32")
    vector /= np.linalg.norm(vector)
    results = faiss_service.search(vector, top_k=5)
    assert len(results) == 5


def test_search_fields(faiss_service):
    vector = np.random.randn(384).astype("float32")
    vector /= np.linalg.norm(vector)
    results = faiss_service.search(vector, top_k=3)
    for r in results:
        assert "quote_id" in r
        assert "distance" in r
        assert isinstance(r["quote_id"], int)
        assert isinstance(r["distance"], float)


def test_search_top_k_capped(faiss_service):
    vector = np.random.randn(384).astype("float32")
    vector /= np.linalg.norm(vector)
    results = faiss_service.search(vector, top_k=999)
    assert len(results) == faiss_service.size
