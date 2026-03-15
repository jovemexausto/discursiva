from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Postgres
    database_url: str = "postgresql://discursiva:discursiva@localhost:5432/discursiva"

    # S3 / LocalStack
    s3_bucket: str = "discursiva-submissions"
    s3_endpoint_url: str | None = "http://localhost:4566"
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"
    aws_region: str = "us-east-1"

    # SQS / LocalStack
    sqs_queue_url: str = "http://localhost:4566/000000000000/corrections-queue"
    sqs_endpoint_url: str | None = "http://localhost:4566"

    # Worker
    worker_poll_interval: int = 3

    model_config = SettingsConfigDict(env_file=".env.local", extra="ignore")


settings = Settings()
