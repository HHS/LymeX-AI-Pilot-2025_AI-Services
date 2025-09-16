from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger


class Environment(BaseSettings):
    mongo_uri: str = Field(...)
    mongo_db: str = Field(...)

    redis_host: str
    redis_port: str = Field(6379)
    redis_db: str = Field(0)

    minio_internal_endpoint: str
    minio_root_user: str
    minio_root_password: str
    minio_bucket: str

    qdrant_url: str = Field("http://localhost")
    qdrant_port: int = Field(6333)

    openai_api_key: str = Field(...)
    openai_model: str = Field("gpt-4.1")
    # openai_model: str = Field("o3")

    competitive_analysis_number_of_system_search_documents: int = Field(3)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


environment = Environment()

logger.info("Environment variables loaded successfully.")
