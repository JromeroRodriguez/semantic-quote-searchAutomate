"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Runtime configuration. Overridable via environment or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Models
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Retrieval
    top_k: int = 15
    final_results: int = 3
    max_query_length: int = 500

    # Data paths
    quotes_path: Path = PROJECT_ROOT / "data" / "quotes.json"
    faiss_index_path: Path = PROJECT_ROOT / "data" / "quotes.index"
    metadata_path: Path = PROJECT_ROOT / "data" / "metadata.json"

    # Model loading
    device: str | None = None  # None -> auto (CPU when no GPU present)
    model_dtype: str = "float32"  # float32 | float16 | bfloat16

    # Ollama LLM integration
    ollama_url: str = "http://localhost:11434/api/generate"
    ollama_model: str = "llama3.2"


@lru_cache
def get_settings() -> Settings:
    return Settings()
