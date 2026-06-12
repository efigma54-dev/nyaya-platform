# backend/app/core/config.py

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    APP_SECRET_KEY: str
    CORS_ORIGINS: str = "http://localhost:3000"

    # Database
    DATABASE_URL: str
    POSTGRES_PASSWORD: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""

    # AI APIs
    GROQ_API_KEY: str
    GEMINI_API_KEY: str = Field(
        default="",
        validation_alias=AliasChoices("GEMINI_API_KEY", "GOOGLE_AI_API_KEY"),
    )
    OPENROUTER_API_KEY: str = ""
    CEREBRAS_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    HF_API_KEY: str = Field(
        default="",
        validation_alias=AliasChoices("HF_API_KEY", "HUGGINGFACE_API_KEY"),
    )

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""

    # Derived
    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
