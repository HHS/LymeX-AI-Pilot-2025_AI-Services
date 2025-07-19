from typing import TypeVar

from pydantic import BaseModel
from src.environment import environment
from src.infrastructure.openai import get_openai_client


client = get_openai_client()


T = TypeVar("T", bound=BaseModel)


async def extract_document_data_response_api(
    document_urls: list[str],
    system_instruction: str,
    user_question: str,
    model_class: T,
):
    """
    Extracts data from a list of documents using OpenAI's Response API.
    """
    response = await client.responses.create(
        model=environment.openai_model,
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": system_instruction,
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": user_question,
                    },
                    {
                        "type": "input_file",
                        "file_url": document_url,
                    },
                ],
            },
        ],
    )
