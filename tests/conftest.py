"""Shared fixtures for all test modules."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
QUOTES_PATH = DATA_DIR / "quotes.json"
INDEX_PATH = DATA_DIR / "quotes.index"
METADATA_PATH = DATA_DIR / "metadata.json"


@pytest.fixture(scope="session")
def quotes_data() -> list[dict]:
    with QUOTES_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="session")
def sample_query() -> str:
    return "I feel like everyone is moving forward while I remain stuck."
