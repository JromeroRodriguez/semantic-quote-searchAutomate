"""Tests for the scraper module."""

from backend.app.utils.text import clean_text


def test_clean_text_removes_curly_quotes():
    text = "\u201cHello\u201d \u2018world\u2019"
    assert clean_text(text) == "Hello world"


def test_clean_text_normalizes_whitespace():
    text = "  too   many    spaces  "
    assert clean_text(text) == "too many spaces"


def test_clean_text_strips():
    text = "  padded  "
    assert clean_text(text) == "padded"


def test_clean_text_empty():
    assert clean_text("") == ""


def test_clean_text_plain():
    assert clean_text("simple text") == "simple text"
