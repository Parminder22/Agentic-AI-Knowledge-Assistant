"""
Basic tests — run with: pytest tests/
"""
import pytest
from app.ingestion.chunker import chunk_text
from app.ingestion.cleaner import clean_text
from app.utils.helpers import generate_session_id, truncate_text


def test_chunk_text_basic():
    text = " ".join([f"word{i}" for i in range(1000)])
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert all(isinstance(c, str) for c in chunks)


def test_chunk_text_empty():
    chunks = chunk_text("", chunk_size=100, overlap=10)
    assert chunks == []


def test_clean_text():
    dirty = "Hello   \n\n\n\nWorld   "
    result = clean_text(dirty)
    assert "Hello" in result
    assert "\n\n\n" not in result


def test_generate_session_id():
    sid = generate_session_id()
    assert isinstance(sid, str)
    assert len(sid) == 36  # UUID format


def test_truncate_text():
    long_text = "a" * 1000
    result = truncate_text(long_text, max_chars=100)
    assert len(result) <= 103  # 100 + "..."
    assert result.endswith("...")
