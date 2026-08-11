"""Tests for dataset validity."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

QUOTES_PATH = Path(__file__).resolve().parents[1] / "data" / "quotes.json"


@pytest.fixture(scope="module")
def data():
    with QUOTES_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def test_valid_json(data):
    assert isinstance(data, list)
    assert len(data) > 0


def test_required_fields(data):
    for record in data:
        assert "id" in record, f"missing 'id' in record {record}"
        assert "author" in record, f"missing 'author' in record {record}"
        assert "quote" in record, f"missing 'quote' in record {record}"
        assert record["author"], f"empty author in record {record['id']}"
        assert record["quote"], f"empty quote in record {record['id']}"


def test_ids_are_unique(data):
    ids = [r["id"] for r in data]
    assert len(ids) == len(set(ids)), "duplicate IDs found"


def test_no_duplicates(data):
    seen: set[str] = set()
    for record in data:
        key = record["quote"].lower().strip()
        assert key not in seen, f"duplicate quote text: {record['quote'][:60]}"
        seen.add(key)
