from pathlib import Path

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
    database_url: str # must exist in the .env file with no default

    # Google OAuth settings
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str

    # session cookie settings
    session_middleware_secret: str = "change-me"
    session_cookie_name: str = "bookmemory_session"
    session_ttl_days: int = 7
    cookie_secure: bool = False
    cookie_samesite: str = "lax"  # lax|strict|none
    cookie_domain: str | None = None # can be empty locally


settings = Settings()
