from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Medical Document Intelligence API"
    APP_VERSION: str = "0.1.0"

    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "medragbucket"
    S3_RAW_PREFIX: str = "raw/"

    BEDROCK_MODEL_ID: str = "amazon.nova-micro-v1:0"
    BEDROCK_MAX_TOKENS: int = 512
    BEDROCK_TEMPERATURE: float = 0.0

    TEXTRACT_FEATURES: list[str] = ["FORMS", "TABLES"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()