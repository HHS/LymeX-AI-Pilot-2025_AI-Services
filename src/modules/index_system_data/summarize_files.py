import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import json

from loguru import logger
from openai import OpenAIError
from pydantic import BaseModel

from src.infrastructure.openai import get_openai_client


class FileProductName(BaseModel):
    file_name: str
    product_name: str


class FileSummary(BaseModel):
    files: list[FileProductName]
    summary: str


async def summarize_files(paths: list[Path], timeout: int = 300) -> FileSummary:
    """x
    Upload all PDFs in `paths` to a single OpenAI assistant and return a FileSummary
    containing a per-file product name (from GPT) and overall summary.
    """
    if not paths:
        return FileSummary(files=[], summary="No documents to summarize.")
    client = get_openai_client()
    uploaded_ids = []

    # Upload every file
    for path in paths:
        logger.info(f"Uploading file: {path.name}")
        with open(path, "rb") as f:
            file_obj = client.files.create(file=f, purpose="assistants")
        uploaded_ids.append(file_obj.id)
        logger.info(f"Uploaded {path.name} as {file_obj.id}")

    # Create the assistant with clear instructions for JSON output
    assistant = client.beta.assistants.create(
        instructions=(
            "You are an FDA subject-matter expert. For each attached PDF device form, "
            "extract the product name and the file name. Then, provide:\n"
            "1. A list called 'files', with one object per file containing 'file_name' and 'product_name'.\n"
            "2. A field called 'summary', which is a concise 5-7 sentence summary focusing on the devices’ overall purpose and key features.\n"
            "Return your answer strictly as JSON, e.g.:\n"
            "{\n"
            '  "files": [\n'
            '    {"file_name": "example1.pdf", "product_name": "Example Product 1"},\n'
            '    {"file_name": "example2.pdf", "product_name": "Example Product 2"}\n'
            "  ],\n"
            '  "summary": "Combined summary here."\n'
            "}"
        ),
        model="gpt-4o-mini",
        tools=[{"type": "file_search"}],
    )
    assistant_id = assistant.id
    logger.info(f"Assistant created: {assistant_id}")

    try:
        # Start thread and send the request
        thread = client.beta.threads.create()
        thread_id = thread.id
        attachments = [
            {"file_id": fid, "tools": [{"type": "file_search"}]} for fid in uploaded_ids
        ]
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=(
                "Read all attached PDFs and respond with a JSON including: "
                "1) 'files' (list of file_name and extracted product_name per file), "
                "2) 'summary' (overall combined summary)."
            ),
            attachments=attachments,
        )
        logger.info(
            f"Thread {thread_id} initiated with {len(uploaded_ids)} attachments."
        )

        # Run the assistant and poll for completion
        run = client.beta.threads.runs.create(
            thread_id=thread_id, assistant_id=assistant_id
        )
        run_id = run.id
        deadline = datetime.utcnow() + timedelta(seconds=timeout)
        while datetime.utcnow() < deadline:
            status = client.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=run_id
            ).status
            if status == "completed":
                break
            if status == "failed":
                raise OpenAIError("Assistant run failed")
            await asyncio.sleep(5)
        else:
            raise OpenAIError("Assistant run timed out")

        # Retrieve and parse the JSON response
        messages = client.beta.threads.messages.list(thread_id=thread_id).data
        response = next(
            (m.content[0].text.value for m in messages if m.role == "assistant"), None
        )
        if not response:
            raise OpenAIError("No response from assistant")

        logger.debug(f"Raw assistant response: {response}")

        # Parse JSON from GPT output (strip non-JSON if needed)
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        json_str = response[json_start:json_end]
        result = json.loads(json_str)

        files = [FileProductName(**f) for f in result.get("files", [])]
        summary = result.get("summary", "")

    finally:
        # Cleanup all resources
        for fid in uploaded_ids:
            client.files.delete(fid)
        client.beta.assistants.delete(assistant_id)
        logger.info("Cleanup: deleted all files and assistant.")

    logger.info(f"Final summary for [{', '.join([p.name for p in paths])}]: {summary}")
    return FileSummary(files=files, summary=summary)
