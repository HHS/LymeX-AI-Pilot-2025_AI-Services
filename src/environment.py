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

    openai_api_key: str = Field(..., env="OPENAI_API_KEY")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


environment = Environment()

print("Environment variables loaded successfully.")
logger.info("Environment variables loaded successfully.")
