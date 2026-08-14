"""Application configuration via pydantic-settings.

All secrets come from environment variables (or a local ``.env``) only — never
hardcoded, never committed. Non-secret defaults are provided so the app and the
test-suite are importable without a fully populated environment.
"""
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Datastores -------------------------------------------------------
    database_url: str = "postgresql+asyncpg://veritas:veritas@localhost:5432/veritas"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "veritas-neo4j"

    # --- LLM --------------------------------------------------------------
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    llm_max_tokens: int = 4096

    # --- Auth -------------------------------------------------------------
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 12
    demo_username: str = "demo"
    demo_password: str = "veritas"

    # --- Storage / app ----------------------------------------------------
    storage_dir: str = "./uploads"
    cors_origins: list[str] = ["http://localhost:3000"]
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, value: object) -> object:
        # Accept a comma-separated string in addition to a JSON list.
        if isinstance(value, str) and not value.strip().startswith("["):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in {"production", "prod"}

    @property
    def llm_enabled(self) -> bool:
        return bool(self.anthropic_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
