"""Tests for the FastAPI search endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from backend.app.main import app
    with TestClient(app) as c:
        yield c


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_valid_search(client):
    response = client.post(
        "/api/v1/search",
        json={"query": "I feel stuck while everyone else moves forward"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) <= 3


def test_search_result_fields(client):
    response = client.post(
        "/api/v1/search",
        json={"query": "finding peace in nature"},
    )
    assert response.status_code == 200
    for result in response.json()["results"]:
        assert "id" in result
        assert "quote" in result
        assert "author" in result


def test_empty_query(client):
    response = client.post("/api/v1/search", json={"query": ""})
    assert response.status_code == 422


def test_missing_query(client):
    response = client.post("/api/v1/search", json={})
    assert response.status_code == 422


def test_long_query(client):
    long_query = "a" * 600
    response = client.post("/api/v1/search", json={"query": long_query})
    assert response.status_code == 400


def test_get_root_returns_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
