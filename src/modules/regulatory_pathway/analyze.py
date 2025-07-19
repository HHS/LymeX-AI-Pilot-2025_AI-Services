import asyncio
from datetime import datetime, timezone
from io import BytesIO
from fastapi import HTTPException
import httpx
from src.environment import environment
from loguru import logger
from pydantic import BaseModel
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential
from src.infrastructure.openai import get_openai_client
from src.modules.regulatory_pathway.model import AnalyzeRegulatoryPathwayProgress
from src.modules.product_profile.storage import get_product_profile_documents
from src.modules.regulatory_pathway.model import RegulatoryPathway
from src.infrastructure.redis import redis_client
from src.utils.parse_openai_json import parse_openai_json
from src.utils.prompt import model_to_schema


class AnalyzeProgress:
    initialized = False
    progress: AnalyzeRegulatoryPathwayProgress

    async def initialize(self, product_id: str, total_files: int):
        existing_progress = await AnalyzeRegulatoryPathwayProgress.find_one(
            AnalyzeRegulatoryPathwayProgress.product_id == product_id,
        )
        if existing_progress:
            self.progress = existing_progress
            self.progress.product_id = product_id
            self.progress.total_files = total_files
            self.progress.processed_files = 0
            self.progress.updated_at = datetime.now(timezone.utc)
        else:
            self.progress = AnalyzeRegulatoryPathwayProgress(
                product_id=product_id,
                total_files=total_files,
                processed_files=0,
                updated_at=datetime.now(timezone.utc),
            )
        await self.progress.save()
        self.initialized = True
        logger.info(
            f"Initialized progress for product {product_id} with total files {total_files}"
        )

    async def increase(self, count: int = 1):
        if not self.initialized:
            raise HTTPException(
                status_code=500,
                detail="Progress not initialized. Call initialize() first.",
            )
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


def build_regulatory_pathway_instructions(RegulatoryPathway: type[BaseModel]) -> str:
    schema_str = model_to_schema(RegulatoryPathway)
    prompt = f"""
You are an expert at extracting structured information from regulatory and product documentation for medical devices.

Your task:
- Read and analyze all uploaded PDF documents.
- Extract all relevant information and return a JSON object that exactly matches the following RegulatoryPathway schema.
- Only include fields present in the schema, matching their types and structure.

# RegulatoryPathway JSON Schema

{schema_str}

# Output
Return only the final JSON object matching the schema above, ready for deserialization into the RegulatoryPathway model.

Strictly output valid JSON.
"""
    return prompt.strip()


async def analyze_regulatory_pathway(product_id: str) -> None:
    lock = redis_client.lock(
        f"NOIS2:Background:AnalyzeRegulatoryPathway:AnalyzeLock:{product_id}",
        timeout=100,
    )
    lock_acquired = await lock.acquire(blocking=False)
    if not lock_acquired:
        logger.info(
            f"Lock already acquired for test comparison {product_id}. Skipping analysis."
        )
        return

    docs = await get_product_profile_documents(product_id)
    number_of_documents = len(docs)

    progress = AnalyzeProgress()
    await progress.initialize(product_id, 1)

    try:
        client = get_openai_client()
        file_ids: list[str] = []

        for doc in docs:
            upload_id = None
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10)
            ):
                with attempt:
                    async with httpx.AsyncClient() as http:
                        resp = await http.get(doc.url)
                        resp.raise_for_status()
                    bio = BytesIO(resp.content)
                    bio.name = doc.file_name
                    uploaded = await client.files.create(file=bio, purpose="assistants")
                    upload_id = uploaded.id
            if not upload_id:
                logger.error(f"Failed to upload {doc.file_name}")
                raise HTTPException(502, f"Upload failed for {doc.file_name}")
            file_ids.append(upload_id)
            logger.info(f"Uploaded {doc.file_name} as {upload_id}")

        function_schema = RegulatoryPathway.model_json_schema(by_alias=True)

        assistant = await client.beta.assistants.create(
            instructions=build_regulatory_pathway_instructions(RegulatoryPathway),
            model=environment.openai_model,
            tools=[
                {"type": "file_search"},
                {
                    "type": "function",
                    "function": {
                        "name": "answer_about_pdf",
                        "description": "Return a JSON matching RegulatoryPathway schema.",
                        "parameters": function_schema,
                    },
                },
            ],
        )

        thread = await client.beta.threads.create()
        QUESTION = (
            "Read all uploaded PDF documents and extract all relevant information. "
            "Return a JSON object matching the RegulatoryPathway schema (structure provided in your system instructions). "
            "Include as much detail as possible."
        )
        await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=QUESTION,
            attachments=[
                {"file_id": fid, "tools": [{"type": "file_search"}]} for fid in file_ids
            ],
        )

        run = await client.beta.threads.runs.create(
            thread_id=thread.id, assistant_id=assistant.id
        )
        for _ in range(60):
            run = await client.beta.threads.runs.retrieve(
                thread_id=thread.id, run_id=run.id
            )
            if run.status == "completed":
                break
            if run.status == "failed":
                logger.error(f"Assistant run failed: {run.error}")
                raise HTTPException(502, "Assistant failed")
            if run.status == "requires_action":
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

        # Retrieve assistant message
        msgs = await client.beta.threads.messages.list(thread_id=thread.id)
        result_text = None
        for msg in msgs.data:
            if msg.role == "assistant":
                result_text = msg.content[0].text.value
                break
        if not result_text:
            raise HTTPException(502, "No assistant response found.")

        regulatory_pathway = parse_openai_json(result_text)

        # Cleanup assistant and files
        try:
            await client.beta.assistants.delete(assistant.id)
        except Exception:
            pass
        for fid in file_ids:
            try:
                await client.files.delete(fid)
            except Exception:
                pass

        await RegulatoryPathway.find(
            RegulatoryPathway.product_id == product_id
        ).delete_many()
        record = {**regulatory_pathway, "product_id": product_id}
        await RegulatoryPathway(**record).save()
        logger.info(
            f"Analyzed product profile for product: {product_id}, including {number_of_documents} documents."
        )
        await progress.complete()

    except Exception as exc:
        logger.error(f"Error analyzing {product_id}: {exc}")
        raise
    finally:
        await lock.release()
        logger.info(f"Released lock for product {product_id}")
