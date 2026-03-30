from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://aura:aura@localhost:5433/aura"

    # Auth
    JWT_SECRET: SecretStr = SecretStr("change-me-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # OAuth - GitHub
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: SecretStr = SecretStr("")
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/github/callback"

    # Frontend
    FRONTEND_URL: str = "http://localhost:5173"

    # AWS Bedrock
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: SecretStr | None = None
    BEDROCK_NARRATION_MODEL: str = "anthropic.claude-3-5-haiku-20241022-v1:0"
    BEDROCK_QUEST_MODEL: str = "anthropic.claude-3-5-haiku-20241022-v1:0"

    # App
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    ENVIRONMENT: str = "development"


settings = Settings()
