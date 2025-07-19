import asyncio
from pathlib import Path
from fastapi import HTTPException
from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel
from loguru import logger
from src.environment import environment
from src.infrastructure.openai import get_openai_client
from src.utils.parse_openai_json import parse_openai_json
from src.utils.prompt import model_to_schema
from src.utils.supported_file_extensions import SUPPORTED_FILE_EXTENSIONS


def create_magic_instruction(
    system_instruction: str,
    model_class: type[BaseModel],
) -> str:
    schema_str = model_to_schema(model_class)
    logger.info("Creating magic instruction for model: {}", model_class.__name__)
    return f"""
# Instructions:

{system_instruction}

# Output:

Return a JSON object that matches the schema below. The JSON should be valid and conform to the structure defined by the model class.
Please ensure that all fields are included and that their types match the schema.
And the meaning should be the same as expressed in the comment of each field.

Only return data that available in the documents. Do not infer or assume any data that is not present in the documents.
Words like "unknown", "not available", "not applicable".. should be used if the data is not present in the documents.

Do not include any additional text or explanations, just the JSON object, no code fencing, no comments, no markdown formatting.

Below is the schema for the JSON object:

{schema_str}
"""


def upload_documents(
    client: OpenAI,
    documents: list[Path],
) -> list[str]:
    file_ids = []
    for doc in documents:
        logger.info("Uploading document: {}", doc)
        if doc.suffix.lower() not in SUPPORTED_FILE_EXTENSIONS:
            logger.error("Unsupported file type: {}", doc.suffix)
            raise ValueError(f"Unsupported file type: {doc.suffix}")

        with open(doc, "rb") as f:
            response = client.files.create(file=f, purpose="assistants")
            logger.info("Uploaded file {} with id {}", doc, response.id)
            file_ids.append(response.id)

    logger.info("Uploaded {} documents", len(file_ids))
    return file_ids


async def cleanup_uploaded_files(
    client: AsyncOpenAI,
    file_ids: list[str],
) -> None:
    logger.info("Cleaning up {} uploaded files", len(file_ids))
    for file_id in file_ids:
        try:
            await client.files.delete(file_id)
            logger.info("Deleted file with id {}", file_id)
        except Exception as e:
            logger.error("Error deleting file {}: {}", file_id, e)
            continue


async def extract_documents_data(
    documents: list[Path],
    system_instruction: str,
    user_question: str,
    model_class: type[BaseModel],
):
    logger.info("Starting document extraction for {} documents", len(documents))
    instruction = create_magic_instruction(
        system_instruction=system_instruction,
        model_class=model_class,
    )
    logger.info("Created magic instruction: {}", instruction)

    client = get_openai_client()
    logger.info("Obtained OpenAI client")

    file_ids = upload_documents(await client, documents)

    try:
        function_schema = model_class.model_json_schema(by_alias=True)
        logger.info("Creating assistant with model: {}", environment.openai_model)
        assistant = await client.beta.assistants.create(
            instructions=instruction,
            model=environment.openai_model,
            tools=[
                {"type": "file_search"},
                {
                    "type": "function",
                    "function": {
                        "name": "extract_documents_data",
                        "description": "Extract data from uploaded documents.",
                        "parameters": function_schema,
                    },
                },
            ],
        )
        logger.info("Assistant created with id {}", assistant.id)
        thread = await client.beta.threads.create()
        logger.info("Thread created with id {}", thread.id)
        await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_question,
            attachments=[
                {"file_id": fid, "tools": [{"type": "file_search"}]} for fid in file_ids
            ],
        )
        logger.info("User question sent to thread {}", thread.id)
        run = await client.beta.threads.runs.create(
            thread_id=thread.id, assistant_id=assistant.id
        )
        logger.info("Run started with id {}", run.id)

        for attempt in range(60):
            run = await client.beta.threads.runs.retrieve(
                thread_id=thread.id, run_id=run.id
            )
            logger.info("Run status: {} (attempt {})", run.status, attempt + 1)
            if run.status == "completed":
                logger.info("Run completed")
                break
            elif run.status == "failed":
                logger.error("Run failed")
                raise HTTPException(502, "Run failed")
            elif run.status == "cancelled":
                logger.error("Run cancelled")
                raise HTTPException(502, "Run cancelled")
            elif run.status == "requires_action":
                logger.info("Run requires action, submitting tool outputs")
                logger.info(
                    "Run requires action: submitting tool outputs for tool_calls: {}",
                    run.required_action.submit_tool_outputs.tool_calls,
                )
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = [
                    {"tool_call_id": tc.id, "output": ""} for tc in tool_calls
                ]
                run = await client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs,
                )
            await asyncio.sleep(5)

    finally:
        try:
            logger.info("Deleting assistant with id {}", assistant.id)
            await client.beta.assistants.delete(assistant.id)
        except Exception as e:
            logger.error("Error during assistant cleanup: {}", e)

        try:
            await cleanup_uploaded_files(client, file_ids)
        except Exception as e:
            logger.error("Error during cleanup: {}", e)

    msgs = await client.beta.threads.messages.list(thread_id=thread.id)
    result_text = None
    for msg in msgs.data:
        if msg.role == "assistant":
            result_text = msg.content[0].text.value
            logger.info("Assistant response found")
            break
    if not result_text:
        logger.error("No assistant response found")
        raise HTTPException(502, "No assistant response found.")
    logger.info("Parsing OpenAI JSON response")
    parsed_data = parse_openai_json(result_text)
    logger.info("Document extraction completed successfully")
    data = model_class(**parsed_data)
    return data


if __name__ == "__main__":
    from src.modules.product_profile.schema import ProductProfileSchema
    from src.modules.product_profile.analyze import load_questionnaire_text

    documents = [Path("/Users/macbookpro/Downloads/K203292.pdf")]
    system_instruction = (
        (
            "You are an FDA expert. Use the uploaded PDF files to extract a complete "
            "product profile. Return **only** valid JSON that matches the "
            "ProductProfile schema exactly (no explanations or bullet points). "
            "Required fields now include trade name, model number, generic name, "
            "FDA product code, CFR regulation number, storage conditions, shelf-life, "
            "sterility status, warnings, limitations, contraindications, and a "
            "step-by-step instructions-for-use list. Use the literal string "
            "'not available' for any field you cannot confidently extract."
        ),
    )
    questionnaire_text = load_questionnaire_text()
    user_question = (
        "Please extract a complete product profile using all uploaded FDA PDF "
        "document and return a JSON object matching the ProductProfile schema. "
        "Only include fields present in schema. In particular:\n"
        "• Determine the FDA regulatory pathway ('510(k)', 'De Novo', or 'Premarket Approval (PMA)').\n"
        "• Capture **trade name, model number, and generic name**.\n"
        "• Capture **FDA product code** and **21 CFR regulation number**.\n"
        "• Capture storage conditions, shelf-life, and sterility status if present.\n"
        "• List any warnings, limitations, or contraindications that appear in labeling.\n"
        "• Any software present, single-use or reprocessed single use device "
        "are there any animal-derived materials in the product \n"
        "• Provide a **step-by-step instructions-for-use** list.\n"
        "If an answer is not found, return the field value as 'not available'.\n\n"
        f"{questionnaire_text}"
    )
    result = asyncio.run(
        extract_documents_data(
            documents=documents,
            system_instruction=system_instruction,
            user_question=user_question,
            model_class=ProductProfileSchema,
        )
    )
    print("Extraction completed.")
    print("Result:", result.model_dump_json(indent=4))
