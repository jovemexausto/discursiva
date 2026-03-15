from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Postgres
    database_url: str
    database_pool_min_size: int
    database_pool_max_size: int

    # S3 / LocalStack
    s3_bucket: str
    s3_endpoint_url: str | None
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str

    # SQS / LocalStack
    sqs_queue_url: str
    sqs_endpoint_url: str | None

    # Worker
    worker_poll_interval: int

    model_config = SettingsConfigDict(extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
