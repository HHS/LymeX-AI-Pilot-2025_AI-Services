from openai import OpenAI
from src.environment import environment


def get_openai_client() -> OpenAI:
    openai_client = OpenAI(api_key=environment.openai_api_key)
    return openai_client
