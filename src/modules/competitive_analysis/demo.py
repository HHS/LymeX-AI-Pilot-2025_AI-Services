import openai
import json

import asyncio
from pathlib import Path
from fastapi import HTTPException
from openai import OpenAI
from pydantic import BaseModel
from loguru import logger
from src.environment import environment
from src.infrastructure.openai import get_openai_client
from src.utils.parse_openai_json import parse_openai_json
from src.utils.prompt import model_to_schema
from src.utils.supported_file_extensions import SUPPORTED_FILE_EXTENSIONS

# openai.api_key = "YOUR_OPENAI_API_KEY"

openai.api_key="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"


# Step 1: Upload PDF to OpenAI
def upload_pdf_to_openai(file_path):
    with open(file_path, "rb") as f:
        file = openai.files.create(file=f, purpose="assistants")
    print("i am here")
    return file.id

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

# Step 2: Define the extraction schema
extract_function = {
    "name": "extract_product_profile",
    "description": "Extract product profile from the uploaded PDF",
    "parameters": {
        "type": "object",
        "properties": {
            "product_name": {"type": "string", "description": "Name of the product"},
            "indications": {"type": "string", "description": "Intended use or indications for use"},
            "device_description": {"type": "string", "description": "Detailed description of the device"},
        },
        "required": ["product_name", "indications", "device_description"],
    },
}

# Step 3: Call OpenAI with file_id and the function schema
def extract_info_from_pdf(file_id):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an FDA expert. Use the uploaded PDF to extract a complete product profile. "
                    "Return a JSON object following the defined schema."
                ),
            },
            {
                "role": "user",
                "content": f"Please extract the product profile from the uploaded file.",
                "file_ids": [file_id],
            },
        ],
        functions=[extract_function],
        function_call={"name": "extract_product_profile"},
        # temperature=0,
    )

    return json.loads(response.choices[0].message.function_call.arguments)


# === RUN ===
if __name__ == "__main__":
    pdf_path = "./K203292.pdf"
    file_id = upload_pdf_to_openai(pdf_path)
    extracted_data = extract_info_from_pdf(file_id)
    print("Extracted Info:", json.dumps(extracted_data, indent=2))




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

    file_ids = upload_documents(client, documents)

    try:
        function_schema = model_class.model_json_schema(by_alias=True)
        logger.info("Creating assistant with model: {}", environment.openai_model)
        assistant = client.beta.assistants.create(
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
        thread = client.beta.threads.create()
        logger.info("Thread created with id {}", thread.id)
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_question,
            attachments=[
                {"file_id": fid, "tools": [{"type": "file_search"}]} for fid in file_ids
            ],
        )
        logger.info("User question sent to thread {}", thread.id)
        run = client.beta.threads.runs.create(
            thread_id=thread.id, assistant_id=assistant.id
        )
        logger.info("Run started with id {}", run.id)

        for attempt in range(60):
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
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
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs,
                )
            await asyncio.sleep(5)

    finally:
        try:
            logger.info("Deleting assistant with id {}", assistant.id)
            client.beta.assistants.delete(assistant.id)
        except Exception as e:
            logger.error("Error during assistant cleanup: {}", e)

        try:
            cleanup_uploaded_files(client, file_ids)
        except Exception as e:
            logger.error("Error during cleanup: {}", e)

    msgs = client.beta.threads.messages.list(thread_id=thread.id)
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