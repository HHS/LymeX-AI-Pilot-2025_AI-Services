import json
from pathlib import Path
import time

from openai import AsyncOpenAI

from src.environment import environment
from pydantic import BaseModel, ValidationError
from src.infrastructure.openai import get_openai_client
from src.modules.competitive_analysis.schema import CompetitiveAnalysisDetail


def get_pydantic_schema_prompt(model_class: type[BaseModel]) -> str:
    """
    Generate schema prompt string from Pydantic class fields and their descriptions.
    """
    lines = []
    for name, field in model_class.model_fields.items():
        description = field.description or ""
        lines.append(f"{name}: {description}")
    return "\n".join(lines)


async def get_or_create_fda_assistant(
    client: AsyncOpenAI, assistant_name="FDA Extractor"
):
    # Search for existing assistant
    assistants = list((await client.beta.assistants.list()).data)
    for assistant in assistants:
        if assistant.name == assistant_name:
            return assistant.id

    # Create a new assistant if not found
    assistant = await client.beta.assistants.create(
        name=assistant_name,
        instructions=(
            "Extract all fields in the CompetitiveAnalysisDetail schema from FDA and package insert PDFs. "
            "Return a JSON object with all the fields."
        ),
        tools=[{"type": "file_search"}],
        model=environment.openai_model,
    )
    return assistant.id


async def create_competitive_analysis_detail(
    pdf_path: Path,
) -> CompetitiveAnalysisDetail | None:
    client = get_openai_client()
    ASSISTANT_ID = await get_or_create_fda_assistant(client)
    schema_prompt = get_pydantic_schema_prompt(CompetitiveAnalysisDetail)

    # 1. Upload the file
    with open(pdf_path, "rb") as f:
        file_obj = await client.files.create(file=f, purpose="assistants")
    file_id = file_obj.id

    try:
        # 2. Create a thread & add message with file
        thread = await client.beta.threads.create()
        await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=(
                "Given the attached PDF, extract and return a single JSON object containing ALL of the following fields "
                "according to the schema below. If a field is not found in the document, set its value to 'Not Available'.\n\n"
                "CompetitiveAnalysisDetail schema:\n"
                f"{schema_prompt}\n\n"
                "Only return the JSON object, no extra explanation or formatting."
            ),
            attachments=[{"file_id": file_id, "tools": [{"type": "file_search"}]}],
        )

        # 3. Run the assistant
        run = await client.beta.threads.runs.create(
            thread_id=thread.id, assistant_id=ASSISTANT_ID
        )

        # 4. Wait for completion (polling)
        while True:
            run_status = await client.beta.threads.runs.retrieve(
                thread_id=thread.id, run_id=run.id
            )
            if run_status.status in ["completed", "failed", "cancelled"]:
                break
            time.sleep(2)

        # 5. Fetch the assistant's reply (JSON string)
        if run_status.status == "completed":
            messages = await client.beta.threads.messages.list(thread_id=thread.id)
            for message in messages.data:
                if message.role == "assistant":
                    json_text = message.content[0].text.value
                    try:
                        # Handle extra formatting if GPT adds code block markers
                        if json_text.strip().startswith("```"):
                            json_text = json_text.strip().split("```")[1]
                        data = json.loads(json_text)
                        print(data)
                        return CompetitiveAnalysisDetail(**data)
                    except (json.JSONDecodeError, ValidationError) as e:
                        print("Parsing error:", e)
                        print("Raw model output:", json_text)
                        return None

            return None
        else:
            return None
    finally:
        # 6. Always clean up: delete file from OpenAI storage
        await client.files.delete(file_id)
