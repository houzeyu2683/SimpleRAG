from __future__ import annotations
from functools import lru_cache
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Application
    app_env: str = "development"
    app_secret_key: str
    app_allowed_origins: list[str] = ["http://localhost:5173"]

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # MariaDB
    database_url: str

    # Qdrant
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_grpc_port: int = 6334

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Celery
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"

    # Ollama (LLM only)
    ollama_base_url: str = "http://ollama:11434"
    ollama_llm_model: str = "qwen2.5:7b-instruct-q4_K_M"

    # Embedding (sentence-transformers, runs locally)
    embed_model: str = "BAAI/bge-m3"

    # RAG
    rag_chunk_size: int = 512
    rag_chunk_overlap: int = 64
    rag_retrieval_top_k: int = 5
    rag_rerank_top_n: int = 3
    qdrant_vector_size: int = 1024

    # Storage
    upload_dir: str = "/app/data/uploads"
    data_dir: str = "/app/data"

    # Seed admin
    seed_admin_email: str = "admin@ragsystem.local"
    seed_admin_password: str
    seed_admin_username: str = "admin"

    @computed_field
    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
