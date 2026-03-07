from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Groq (free)
    groq_api_key: str = "gsk-placeholder"
    groq_model: str = "llama-3.3-70b-versatile"

    # Local embeddings via fastembed (no PyTorch needed)
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dimension: int = 384

    # Database
    database_url: str = "sqlite+aiosqlite:///./assistant.db"

    # FAISS
    faiss_index_path: str = "./faiss_store/index.faiss"
    faiss_meta_path: str = "./faiss_store/meta.json"

    # App
    app_name: str = "AI Knowledge Assistant"
    app_version: str = "1.0.0"
    debug: bool = True
    max_upload_size_mb: int = 20
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_results: int = 5

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()