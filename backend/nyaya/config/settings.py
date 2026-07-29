from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    app_secret_key: SecretStr = Field(
        default=SecretStr("dev_secret_replace_me_32bytes_minimum____"), alias="APP_SECRET_KEY"
    )
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://frontend:3000"], alias="CORS_ORIGINS"
    )

    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_user: str = Field(default="nyaya", alias="POSTGRES_USER")
    postgres_password: SecretStr = Field(default=SecretStr("nyaya_dev_pass_2026"), alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="nyaya_platform", alias="POSTGRES_DB")

    qdrant_host: str = Field(default="localhost", alias="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, alias="QDRANT_PORT")
    qdrant_grpc_port: int = Field(default=6334, alias="QDRANT_GRPC_PORT")
    qdrant_collection: str = Field(default="nyaya_sections_v1", alias="QDRANT_COLLECTION")
    qdrant_vector_size: int = Field(default=1024)

    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")

    embedding_model: str = Field(default="BAAI/bge-m3")
    cross_encoder_model: str = Field(default="cross-encoder/ms-marco-MiniLM-L-12-v2")
    rerank_top_k: int = Field(default=50)
    dense_top_k: int = Field(default=50)
    bm25_top_k: int = Field(default=50)
    hybrid_dense_weight: float = Field(default=0.55)
    hybrid_bm25_weight: float = Field(default=0.45)

    citation_validator_threshold: float = Field(default=0.72)
    hallucination_penalty: float = Field(default=0.5)

    access_token_ttl_minutes: int = Field(default=60 * 24 * 7)
    jwt_algorithm: str = Field(default="HS256")

    evidence_dir: str = Field(default="./evidence")

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password.get_secret_value()}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def postgres_sync_dsn(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:"
            f"{self.postgres_password.get_secret_value()}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
