from openai import AsyncOpenAI
from src.environment import environment


def get_openai_client() -> AsyncOpenAI:
    openai_client = AsyncOpenAI(api_key=environment.openai_api_key)
    return openai_client
