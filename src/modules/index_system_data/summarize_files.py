import asyncio
from datetime import datetime, timedelta
from pathlib import Path

from loguru import logger
from openai import OpenAIError

from src.infrastructure.openai import get_openai_client


async def summarize_files(paths: list[Path], timeout: int = 300) -> str:
    """
    Upload all PDFs in `paths` to a single OpenAI assistant and return one concise paragraph
    summarizing their collective purpose and key features.

    Args:
        paths: List of Paths to the PDFs.
        timeout: Seconds to wait before timing out.

    Returns:
        A single-paragraph summary string covering all uploaded documents.
    """
    client = get_openai_client()
    uploaded_ids = []

    # Upload every file
    for path in paths:
        logger.info(f"Uploading file: {path.name}")
        with open(path, "rb") as f:
            file_obj = client.files.create(file=f, purpose="assistants")
        uploaded_ids.append(file_obj.id)
        logger.info(f"Uploaded {path.name} as {file_obj.id}")

    # Create a temporary assistant with combined-summary instructions
    assistant = client.beta.assistants.create(
        instructions=(
            "You are an FDA subject-matter expert. For the attached PDF device form, "
            "provide:\n"
            "1) A concise 5-7 sentence summary focusing on the device’s overall purpose "
            "and key functional features.\n"
            "2) A list of 10–15 general, high-level keywords (avoid numeric values or overly "
            "specific measurements) that capture the main concepts—these will be used to "
            "search for similar devices."
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
                "Please read all attached PDFs and respond with one concise paragraph summarizing "
                "their collective purpose and main functional features."
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
            await asyncio.sleep(2)
        else:
            raise OpenAIError("Assistant run timed out")

        # Retrieve and return the single-paragraph response
        messages = client.beta.threads.messages.list(thread_id=thread_id).data
        response = next(
            (m.content[0].text.value for m in messages if m.role == "assistant"), None
        )
        if not response:
            raise OpenAIError("No response from assistant")
        summary = response.strip()

    finally:
        # Cleanup all resources
        for fid in uploaded_ids:
            client.files.delete(fid)
        client.beta.assistants.delete(assistant_id)
        logger.info("Cleanup: deleted all files and assistant.")

    logger.info(f"Final summary for [{', '.join([p.name for p in paths])}]: {summary}")
    return summary
