"""Tests for BGE reranker."""

from __future__ import annotations

import pytest

from backend.app.services.reranker.bge_service import BGERerankerService


@pytest.fixture(scope="module")
def reranker_service():
    return BGERerankerService("cross-encoder/ms-marco-MiniLM-L-6-v2", dtype="float32")


def test_rerank_returns_sorted(reranker_service):
    candidates = [
        {"quote_id": 1, "quote": "I love rainy days", "author": "Test"},
        {"quote_id": 2, "quote": "The sun is bright today", "author": "Test"},
    ]
    ranked = reranker_service.rerank("I feel peaceful when it rains", candidates)
    assert len(ranked) == 2
    assert ranked[0]["quote_id"] == 1  # rainy should rank higher


def test_rerank_top_3_selection(reranker_service):
    candidates = [
        {"quote_id": i, "quote": f"Quote number {i}", "author": "Test"}
        for i in range(10)
    ]
    ranked = reranker_service.rerank("test query", candidates)
    assert len(ranked) == 10


def test_rerank_empty_candidates(reranker_service):
    ranked = reranker_service.rerank("query", [])
    assert ranked == []
