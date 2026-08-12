"""Tests for the optimizer API endpoint."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from backend.app.main import app
    with TestClient(app) as c:
        yield c


def test_optimizer_endpoint_valid(client):
    response = client.post(
        "/api/v1/optimizer/run",
        json={"max_tokens": 1000},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "receipt" in data
    assert "batches" in data
    assert data["receipt"]["quotes_processed"] > 0
    assert data["receipt"]["batches_created"] > 0


def test_optimizer_endpoint_small_budget(client):
    response = client.post(
        "/api/v1/optimizer/run",
        json={"max_tokens": 100},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["receipt"]["batches_created"] > 1


def test_optimizer_endpoint_invalid_budget(client):
    response = client.post(
        "/api/v1/optimizer/run",
        json={"max_tokens": -1},
    )
    assert response.status_code == 422


def test_optimizer_endpoint_zero_budget(client):
    response = client.post(
        "/api/v1/optimizer/run",
        json={"max_tokens": 0},
    )
    assert response.status_code == 422


def test_optimizer_endpoint_missing_budget(client):
    response = client.post("/api/v1/optimizer/run", json={})
    assert response.status_code == 422


def test_optimizer_batch_fields(client):
    response = client.post(
        "/api/v1/optimizer/run",
        json={"max_tokens": 500},
    )
    assert response.status_code == 200
    data = response.json()
    for batch in data["batches"]:
        assert "batch_id" in batch
        assert "quote_ids" in batch
        assert "quote_count" in batch
        assert "estimated_input_tokens" in batch
        assert batch["quote_count"] == len(batch["quote_ids"])
        assert batch["estimated_input_tokens"] <= 500


def test_optimizer_receipt_fields(client):
    response = client.post(
        "/api/v1/optimizer/run",
        json={"max_tokens": 1000},
    )
    assert response.status_code == 200
    receipt = response.json()["receipt"]
    required = [
        "quotes_processed", "batches_created", "requests_completed",
        "requests_failed", "estimated_input_tokens", "actual_input_tokens",
        "actual_output_tokens", "total_tokens", "token_limit_per_request",
    ]
    for field in required:
        assert field in receipt, f"missing field: {field}"
