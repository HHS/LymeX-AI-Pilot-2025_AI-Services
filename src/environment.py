from pydantic import Field
from pydantic_settings import BaseSettings
from loguru import logger


class Environment(BaseSettings):
    postgres_host: str = Field(..., env="POSTGRES_HOST")
    postgres_port: int = Field(..., env="POSTGRES_PORT")
    postgres_user: str = Field(..., env="POSTGRES_USER")
    postgres_password: str = Field(..., env="POSTGRES_PASSWORD")
    postgres_db: str = Field(..., env="POSTGRES_DB")

    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")


environment = Environment()

print("Environment variables loaded successfully.")
logger.info("Environment variables loaded successfully.")
print(f"Base URL: {environment.base_url}")
print(f"Refresh token: {environment.refresh_token}")
