from openai import AsyncOpenAI, OpenAI
from src.environment import environment


def get_openai_client() -> AsyncOpenAI:
    openai_client = AsyncOpenAI(api_key=environment.openai_api_key)
    return openai_client


def get_openai_client_sync() -> OpenAI:
    """
    Synchronous wrapper for the OpenAI client.
    This is useful for compatibility with synchronous code.
    """
    openai_client = OpenAI(api_key=environment.openai_api_key)
    return openai_client
