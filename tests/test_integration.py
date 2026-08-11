"""Integration test: full pipeline from query to top 3 results."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from backend.app.main import app
    with TestClient(app) as c:
        yield c


@pytest.mark.parametrize("query", [
    "I feel like everyone is moving forward while I remain stuck.",
    "The feeling of peace I get when I watch the rain.",
    "I wonder if the life I built is really the life I wanted.",
    "I am terrified of what the future holds for me.",
    "I am surrounded by people but feel completely alone.",
])
def test_full_pipeline_returns_3_valid_results(client, query):
    response = client.post("/api/v1/search", json={"query": query})
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 3
    for r in results:
        assert "id" in r
        assert "quote" in r
        assert "author" in r
        assert isinstance(r["id"], int)
        assert isinstance(r["quote"], str) and len(r["quote"]) > 0
        assert isinstance(r["author"], str) and len(r["author"]) > 0


def test_pipeline_consistency(client):
    """Same query should return the same results."""
    q = "feeling stuck while others advance"
    r1 = client.post("/api/v1/search", json={"query": q}).json()
    r2 = client.post("/api/v1/search", json={"query": q}).json()
    assert [x["id"] for x in r1["results"]] == [x["id"] for x in r2["results"]]
