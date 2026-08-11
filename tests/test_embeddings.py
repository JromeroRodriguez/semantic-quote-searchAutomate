"""Tests for Jina embedding generation."""

from __future__ import annotations

import numpy as np
import pytest

from backend.app.services.embeddings.jina_service import EmbeddingService


@pytest.fixture(scope="module")
def embedding_service():
    return EmbeddingService("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", dtype="float32")


def test_embed_passages_shape(embedding_service):
    texts = ["Hello world", "Test sentence"]
    embeddings = embedding_service.embed_passages(texts)
    assert embeddings.shape[0] == 2
    assert embeddings.shape[1] == 384  # MiniLM-L12 dim


def test_embed_query_shape(embedding_service):
    embedding = embedding_service.embed_query("Test query")
    assert embedding.shape == (384,)


def test_embeddings_are_normalized(embedding_service):
    texts = ["A test passage"]
    embeddings = embedding_service.embed_passages(texts)
    norms = np.linalg.norm(embeddings, axis=1)
    np.testing.assert_allclose(norms, 1.0, atol=1e-5)


def test_query_embedding_normalized(embedding_service):
    emb = embedding_service.embed_query("Test")
    assert abs(np.linalg.norm(emb) - 1.0) < 1e-5
