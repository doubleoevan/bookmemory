from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

from bookmemory.services.ai.providers import AIProviderType

BASE_DIR = Path(__file__).resolve().parents[3]  # apps/api/


class Settings(BaseSettings):
    """Loads the application configuration from environment variables."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )

    # app settings
    app_env: str = "local"
    api_base_url: str = "http://localhost:8000"
    web_base_url: str = "http://localhost:5174"

    # CORS settings
    cors_origins: str = "http://localhost:5174"

    # database settings
    database_url: str = ""  # must exist in the .env file with no default

    # Google OAuth settings
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""

    # session cookie settings
    session_cookie_name: str = "bookmemory_session"
    session_ttl_days: int = 7
    cookie_secure: bool = False
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    cookie_domain: str | None = None

    # ai provider settings
    embedding_provider: AIProviderType = "openai"
    description_provider: AIProviderType = "openai"
    summary_provider: AIProviderType = "openai"

    # OpenAI settings
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_dim: int = 1536
    openai_embed_max_concurrency: int = 6
    openai_embed_batch_size: int = 64
    openai_chat_model: str = "gpt-5-mini"
    openai_description_max_concurrency: int = 4
    openai_summary_max_concurrency: int = 1

    # Fetching concurrency limits
    http_fetch_max_concurrency: int = 20
    playwright_fetch_max_concurrency: int = 2


settings = Settings()
