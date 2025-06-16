import asyncio
from datetime import datetime, timezone
from io import BytesIO
from uuid import uuid4

import httpx
from fastapi import HTTPException
from loguru import logger
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential

from src.infrastructure.openai import get_openai_client
from src.infrastructure.redis import redis_client
from src.modules.product_profile.model import ProductProfile, AnalyzeProductProfileProgress
from src.modules.product_profile.storage import get_product_profile_documents
from src.utils.parse_openai_json import parse_openai_json

class AnalyzeProgress:
    def __init__(self):
        self.progress: AnalyzeProductProfileProgress | None = None

    async def initialize(self, product_id: str, total_files: int):
        existing = await AnalyzeProductProfileProgress.find_one(
            AnalyzeProductProfileProgress.product_id == product_id
        )
        now = datetime.now(timezone.utc)
        if existing:
            existing.total_files = total_files
            existing.processed_files = 0
            existing.updated_at = now
            self.progress = existing
        else:
            self.progress = AnalyzeProductProfileProgress(
                product_id=product_id,
                total_files=total_files,
                processed_files=0,
                updated_at=now,
            )
        await self.progress.save()
        logger.info(f"Progress initialized for {product_id}: {total_files} files")

    async def increment(self, count: int = 1):
        if not self.progress:
            raise HTTPException(500, "Progress must be initialized first.")
        self.progress.processed_files += count
        self.progress.updated_at = datetime.now(timezone.utc)
        await self.progress.save()

    async def complete(self):
        if not self.progress:
            return
        self.progress.processed_files = self.progress.total_files
        self.progress.updated_at = datetime.now(timezone.utc)
        await self.progress.save()
        logger.info(f"Progress complete for {self.progress.product_id}")

async def analyze_product_profile(product_id: str) -> None:
    lock = redis_client.lock(f"analyze_lock:{product_id}", timeout=60)
    if not await lock.acquire(blocking=False):
        logger.warning(f"Analysis already running for {product_id}")
        return

    try:
        docs = await get_product_profile_documents(product_id)
        total = len(docs)
        progress = AnalyzeProgress()
        await progress.initialize(product_id, total)

        client = get_openai_client()
        file_ids: list[str] = []

        # Upload each document with retry
        for doc in docs:
            upload_id = None
            async for attempt in AsyncRetrying(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10)):
                with attempt:
                    async with httpx.AsyncClient() as http:
                        resp = await http.get(doc.url)
                        resp.raise_for_status()
                    bio = BytesIO(resp.content)
                    bio.name = doc.file_name
                    uploaded = client.files.create(file=bio, purpose="assistants")
                    upload_id = uploaded.id
            if not upload_id:
                logger.error(f"Failed to upload {doc.file_name}")
                raise HTTPException(502, f"Upload failed for {doc.file_name}")
            file_ids.append(upload_id)
            await progress.increment()
            logger.info(f"Uploaded {doc.file_name} as {upload_id}")

        # Build schema for function tool
        function_schema = ProductProfile.model_json_schema(by_alias=True)

        # Create an assistant with file_search and function tool
        assistant = client.beta.assistants.create(
            instructions="You are an FDA expert. Use provided PDF files to extract a complete product profile.",
            model="gpt-4.1",
            tools=[
                {"type": "file_search"},
                {"type": "function", "function": {
                    "name": "answer_about_pdf",
                    "description": "Return a JSON matching ProductProfile schema.",
                    "parameters": function_schema,
                }}
            ],
        )

        # Start a thread and send user question
        thread = client.beta.threads.create()
        QUESTION = (
            "Please read all uploaded PDF documents and return a JSON object matching the ProductProfile schema. "
            "Only include fields present in schema."
        )
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=QUESTION,
            attachments=[{"file_id": fid, "tools": [{"type": "file_search"}]} for fid in file_ids],
        )

        # Run the assistant and poll for completion
        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id)
        for _ in range(60):  # up to 5 minutes
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run.status == "completed":
                break
            if run.status == "failed":
                logger.error(f"Assistant run failed: {run.error}")
                raise HTTPException(502, "Assistant failed")
            if run.status == "requires_action":
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = [{"tool_call_id": tc.id, "output": ""} for tc in tool_calls]
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs,
                )
            await asyncio.sleep(5)

        # Retrieve assistant message
        msgs = client.beta.threads.messages.list(thread_id=thread.id)
        result_text = None
        for msg in msgs.data:
            if msg.role == "assistant":
                result_text = msg.content[0].text.value
                break
        if not result_text:
            raise HTTPException(502, "No assistant response found.")

        profile = parse_openai_json(result_text)

        # Cleanup assistant and files
        try:
            client.beta.assistants.delete(assistant.id)
        except Exception:
            pass
        for fid in file_ids:
            try:
                client.files.delete(fid)
            except Exception:
                pass

        # Save profile
        await ProductProfile.find(ProductProfile.product_id == product_id).delete_many()
        record = {**profile, "product_id": product_id}
        await ProductProfile(**record).save()

        await progress.complete()
        logger.success(f"Saved product profile for {product_id}")

    except Exception as exc:
        logger.error(f"Error analyzing {product_id}: {exc}")
        raise

    finally:
        try:
            await lock.release()
        except Exception:
            pass
