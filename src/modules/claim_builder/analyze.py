import asyncio
from datetime import datetime, timezone
from enum import Enum
from io import BytesIO
from typing import Dict, List, Union, get_args, get_origin
from fastapi import HTTPException
import httpx
from loguru import logger
from pydantic import BaseModel
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential
from src.infrastructure.openai import get_openai_client
from src.modules.claim_builder.model import AnalyzeClaimBuilderProgress, ClaimBuilder
from src.infrastructure.redis import redis_client
from src.modules.product_profile.storage import get_product_profile_documents
from src.utils.parse_openai_json import parse_openai_json


class AnalyzeProgress:
    initialized = False
    progress: AnalyzeClaimBuilderProgress

    async def initialize(self, product_id: str, total_files: int):
        existing_progress = await AnalyzeClaimBuilderProgress.find_one(
            AnalyzeClaimBuilderProgress.product_id == product_id,
        )
        if existing_progress:
            self.progress = existing_progress
            self.progress.product_id = product_id
            self.progress.total_files = total_files
            self.progress.processed_files = 0
            self.progress.updated_at = datetime.now(timezone.utc)
        else:
            self.progress = AnalyzeClaimBuilderProgress(
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


def get_enum_values(enum_type):
    return [e.value for e in enum_type]


def field_type_repr(field_type):
    origin = get_origin(field_type)
    if origin is Union:
        args = get_args(field_type)
        if type(None) in args:
            other = [a for a in args if a is not type(None)]
            return f"{field_type_repr(other[0])} | null"
        else:
            return " | ".join([field_type_repr(a) for a in args])
    if origin is list or origin is List:
        item_type = get_args(field_type)[0]
        return f"list[{field_type_repr(item_type)}]"
    if origin is dict or origin is Dict:
        key_type, val_type = get_args(field_type)
        return f"dict[{field_type_repr(key_type)}, {field_type_repr(val_type)}]"
    if hasattr(field_type, "__fields__"):
        return "object"
    if isinstance(field_type, type) and issubclass(field_type, Enum):
        return (
            "enum(" + " | ".join([repr(v) for v in get_enum_values(field_type)]) + ")"
        )
    if field_type is str:
        return "string"
    if field_type is int:
        return "int"
    if field_type is bool:
        return "boolean"
    if field_type is float:
        return "float"
    if field_type is datetime:
        return "ISO8601 datetime string"
    return str(field_type)


def model_to_schema(model: type[BaseModel], indent: int = 0) -> str:
    pad = "  " * indent
    lines = ["{"]
    for name, field in model.model_fields.items():
        typ = field.annotation
        if hasattr(typ, "__fields__"):  # Nested model
            value = model_to_schema(typ, indent + 1)
        elif get_origin(typ) in [list, List]:
            subtyp = get_args(typ)[0]
            if hasattr(subtyp, "__fields__"):
                value = f"[{model_to_schema(subtyp, indent + 2)}{pad}  ]"
            elif isinstance(subtyp, type) and issubclass(subtyp, Enum):
                value = f"list[{field_type_repr(subtyp)}]"
            else:
                value = f"list[{field_type_repr(subtyp)}]"
        elif isinstance(typ, type) and issubclass(typ, Enum):
            value = field_type_repr(typ)
        else:
            value = field_type_repr(typ)
        lines.append(f'{pad}  "{name}": {value},')
    lines.append(pad + "}")
    return "\n".join(lines)


def build_claim_builder_instructions(ClaimBuilder: type[BaseModel]) -> str:
    schema_str = model_to_schema(ClaimBuilder)
    prompt = f"""
You are an expert at extracting structured information from regulatory and product documentation for medical devices.

Your task:
- Read and analyze all uploaded PDF documents.
- Extract all relevant information and return a JSON object that exactly matches the following ClaimBuilder schema.
- Only include fields present in the schema, matching their types and structure.

# ClaimBuilder JSON Schema

{schema_str}

# Output
Return only the final JSON object matching the schema above, ready for deserialization into the ClaimBuilder model.

Strictly output valid JSON.
"""
    return prompt.strip()


async def analyze_claim_builder(product_id: str) -> None:
    lock = redis_client.lock(
        f"NOIS2:Background:AnalyzeClaimBuilder:AnalyzeLock:{product_id}",
        timeout=100,
    )
    lock_acquired = await lock.acquire(blocking=False)
    if not lock_acquired:
        logger.info(
            f"Task is already running for product {product_id}. Skipping analysis."
        )
        return

    docs = await get_product_profile_documents(product_id)
    number_of_documents = len(docs)

    progress = AnalyzeProgress()
    await progress.initialize(product_id, number_of_documents)

    try:
        await ClaimBuilder.find(
            ClaimBuilder.product_id == product_id,
        ).delete_many()

        client = get_openai_client()
        file_ids: list[str] = []

        # Upload each document with retry
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
                    uploaded = client.files.create(file=bio, purpose="assistants")
                    upload_id = uploaded.id
            if not upload_id:
                logger.error(f"Failed to upload {doc.file_name}")
                raise HTTPException(502, f"Upload failed for {doc.file_name}")
            file_ids.append(upload_id)
            logger.info(f"Uploaded {doc.file_name} as {upload_id}")

        # Build schema for function tool
        function_schema = ClaimBuilder.model_json_schema(by_alias=True)

        # Create an assistant with file_search and function tool
        assistant = client.beta.assistants.create(
            instructions=build_claim_builder_instructions(ClaimBuilder),
            model="gpt-4.1",
            tools=[
                {"type": "file_search"},
                {
                    "type": "function",
                    "function": {
                        "name": "answer_about_pdf",
                        "description": "Return a JSON matching ClaimBuilder schema.",
                        "parameters": function_schema,
                    },
                },
            ],
        )

        # Start a thread and send user question
        thread = client.beta.threads.create()
        QUESTION = (
            "Read all uploaded PDF documents and extract all relevant information. "
            "Return a JSON object matching the ClaimBuilder schema (structure provided in your system instructions). "
            "Include as much detail as possible."
        )
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=QUESTION,
            attachments=[
                {"file_id": fid, "tools": [{"type": "file_search"}]} for fid in file_ids
            ],
        )

        # Run the assistant and poll for completion
        run = client.beta.threads.runs.create(
            thread_id=thread.id, assistant_id=assistant.id
        )
        for _ in range(60):  # up to 5 minutes
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
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

        claim_builder = parse_openai_json(result_text)

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

        await ClaimBuilder.find(ClaimBuilder.product_id == product_id).delete_many()
        record = {**claim_builder, "product_id": product_id}
        await ClaimBuilder(**record).save()
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
