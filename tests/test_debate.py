"""Tests for the debate service and API endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.services.debate.debate_service import DebateService, FALLBACK_MESSAGE


class DummySearchServiceSuccess:
    def search(self, query: str) -> list[dict[str, any]]:
        return [
            {
                "quote_id": 1,
                "quote": "La imaginación es más importante que el conocimiento.",
                "author": "Albert Einstein",
            },
            {
                "quote_id": 2,
                "quote": "La imaginación nos lleva a mundos que nunca existieron.",
                "author": "Carl Sagan",
            },
        ]


class DummySearchServiceEmpty:
    def search(self, query: str) -> list[dict[str, any]]:
        return []


def test_debate_service_success():
    search_service = DummySearchServiceSuccess()
    service = DebateService(search_service=search_service)
    result = service.debate("¿Es más importante el conocimiento o la imaginación?")

    assert result["success"] is True
    assert "Albert Einstein" in result["essay"]
    assert "Carl Sagan" in result["essay"]
    assert len(result["sources"]) == 2
    assert result["sources"][0]["author"] == "Albert Einstein"


def test_debate_service_fallback():
    search_service = DummySearchServiceEmpty()
    service = DebateService(search_service=search_service)
    result = service.debate("Pregunta sin referencias posibles en el dataset.")

    assert result["success"] is False
    assert result["essay"] == FALLBACK_MESSAGE
    assert result["sources"] == []


@pytest.fixture(scope="module")
def client():
    from backend.app.main import app
    with TestClient(app) as c:
        yield c


def test_debate_endpoint_valid(client):
    response = client.post(
        "/api/v1/debate",
        json={"query": "Is imagination more important than knowledge?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "essay" in data
    assert "sources" in data


def test_debate_endpoint_empty_query(client):
    response = client.post("/api/v1/debate", json={"query": ""})
    assert response.status_code == 422
