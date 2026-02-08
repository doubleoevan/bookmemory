from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

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
    session_middleware_secret: str = "change-me"
    session_cookie_name: str = "bookmemory_session"
    session_ttl_days: int = 7
    cookie_secure: bool = False
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    cookie_domain: str | None = None

    # OpenAI settings
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_dim: int = 1536

    # Embedding concurrency limits
    embed_max_concurrency: int = 4
    embed_batch_size: int = 64

    # Fetching concurrency limits
    http_fetch_max_concurrency: int = 20
    playwright_fetch_max_concurrency: int = 2


settings = Settings()
