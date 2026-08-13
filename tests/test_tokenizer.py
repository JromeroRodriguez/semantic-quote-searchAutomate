"""Tests for the tokenizer module."""

from backend.app.services.optimizer.tokenizer import Tokenizer


def test_tokenizer_empty_string():
    t = Tokenizer()
    assert t.count("") == 0


def test_tokenizer_short_quote():
    t = Tokenizer()
    count = t.count("Hello world")
    assert count > 0
    assert count < 20


def test_tokenizer_long_quote():
    t = Tokenizer()
    text = "The only way to do great work is to love what you do. " * 10
    count = t.count(text)
    assert count > 50


def test_tokenizer_unicode():
    t = Tokenizer()
    count = t.count("La imaginación es más importante que el conocimiento.")
    assert count > 0


def test_tokenizer_japanese():
    t = Tokenizer()
    count = t.count("知識は力なり。")
    assert count > 0


def test_tokenizer_batch():
    t = Tokenizer()
    texts = ["Hello", "World", "Test quote here"]
    counts = t.count_batch(texts)
    assert len(counts) == 3
    assert all(c > 0 for c in counts)


def test_tokenizer_caches():
    t1 = Tokenizer()
    t2 = Tokenizer()
    c1 = t1.count("test")
    c2 = t2.count("test")
    assert c1 == c2
