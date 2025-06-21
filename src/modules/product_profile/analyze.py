import asyncio
from datetime import datetime, timezone
from io import BytesIO

import httpx
from fastapi import HTTPException
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from src.infrastructure.openai import get_openai_client
from src.infrastructure.redis import redis_client
from src.modules.product_profile.model import (
    AnalyzeProductProfileProgress,
    ProductProfile,
)
from src.modules.product_profile.schema import ProductProfile as ProfileSchema
from src.modules.product_profile.storage import get_product_profile_documents
from src.utils.parse_openai_json import parse_openai_json


class AnalyzeError(Exception):
    """
    Raised when the OpenAI assistant run fails or times out.
    """

    pass


class FileUploader:
    """
    Downloads documents over HTTP and uploads them to OpenAI, with retry logic.

    Attributes:
        client: OpenAI API client instance.
        _http: HTTPX client for fetching document bytes.
    """

    def __init__(self, client, max_attempts: int = 3):
        """
        Initialize FileUploader.

        Args:
            client: OpenAI API client.
            max_attempts: Number of upload retry attempts.
        """
        self.client = client
        self._http = httpx.AsyncClient(timeout=60)
        self.max_attempts = max_attempts

    async def upload(self, doc) -> str:
        """
        Download `doc.url` and upload to OpenAI.

        Args:
            doc: Object with `url` and `file_name` attributes.

        Returns:
            The OpenAI file ID.
        """
        response = await self._http.get(doc.url)
        response.raise_for_status()
        bio = BytesIO(response.content)
        bio.name = doc.file_name

        upload = await self._retry_upload(bio)
        return upload.id

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def _retry_upload(self, bio: BytesIO):
        """
        Attempt to upload with retries on transient failures.

        Returns:
            OpenAI upload response.
        """
        return self.client.files.create(file=bio, purpose="assistants")

    async def close(self):
        """
        Close the HTTPX client.
        """
        await self._http.aclose()


class AssistantManager:
    """
    Manages lifecycle of an OpenAI assistant:
      1. setup(): creation with tools
      2. submit(): send question with attachments
      3. run(): poll execution and collect response
      4. cleanup(): teardown assistant and files
    """

    def __init__(self, client):
        """
        Args:
            client: OpenAI API client.
        """
        self.client = client
        self.assistant_id: str | None = None
        self.thread_id: str | None = None
        self.run_id: str | None = None

    async def setup(self, schema: dict):
        """
        Create assistant and thread using file_search and function tool.

        Args:
            schema: JSON schema for the ProductProfile function tool.
        """
        assistant = self.client.beta.assistants.create(
            instructions=(
                "You are an FDA expert. Use provided PDF files to extract a "
                "complete product profile."
            ),
            model="gpt-4.1",
            tools=[
                {"type": "file_search"},
                {
                    "type": "function",
                    "function": {
                        "name": "answer_about_pdf",
                        "description": "Return a JSON matching ProductProfile schema.",
                        "parameters": schema,
                    },
                },
            ],
        )
        self.assistant_id = assistant.id
        thread = self.client.beta.threads.create()
        self.thread_id = thread.id

    async def submit(self, file_ids: list[str]):
        """
        Send user query with file attachments.

        Args:
            file_ids: List of uploaded file IDs.
        """
        attachments = [
            {"file_id": fid, "tools": [{"type": "file_search"}]} for fid in file_ids
        ]
        question = (
            "Please read all uploaded PDF documents and return a JSON object "
            "matching the ProductProfile schema. Only include fields present in schema."
        )
        self.client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=question,
            attachments=attachments,
        )

    async def run(self, timeout_sec: int = 300, poll_interval: float = 5) -> str:
        """
        Poll the assistant run until completion or failure.

        Args:
            timeout_sec: Total seconds to wait before timing out.
            poll_interval: Seconds between status checks.

        Returns:
            Assistant message text containing JSON.

        Raises:
            AnalyzeError on failure or timeout.
        """
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id, assistant_id=self.assistant_id
        )
        self.run_id = run.id
        elapsed = 0
        while elapsed < timeout_sec:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread_id, run_id=self.run_id
            )
            if run.status == "completed":
                break
            if run.status == "failed":
                raise AnalyzeError(f"Assistant run failed: {run.error}")
            if run.status == "requires_action":
                self._handle_action(run)
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        else:
            raise AnalyzeError("Assistant run timed out")

        messages = self.client.beta.threads.messages.list(thread_id=self.thread_id)
        for msg in messages.data:
            if msg.role == "assistant":
                return msg.content[0].text.value
        raise AnalyzeError("No assistant response found.")

    def _handle_action(self, run):
        """
        Auto-respond to required tool calls with empty outputs.
        """
        calls = run.required_action.submit_tool_outputs.tool_calls
        outputs = [{"tool_call_id": tc.id, "output": ""} for tc in calls]
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread_id,
            run_id=self.run_id,
            tool_outputs=outputs,
        )

    async def cleanup(self, file_ids: list[str]):
        """
        Delete assistant and uploaded files.

        Args:
            file_ids: File IDs to delete.
        """
        if self.assistant_id:
            try:
                self.client.beta.assistants.delete(self.assistant_id)
            except Exception:
                logger.warning("Failed to delete assistant %s", self.assistant_id)
        for fid in file_ids:
            try:
                self.client.files.delete(fid)
            except Exception:
                logger.warning("Failed to delete file %s", fid)


class ProgressTracker:
    """
    Manages an AnalyzeProductProfileProgress document for progress updates.
    """

    def __init__(self, product_id: str):
        """
        Args:
            product_id: ID to track progress for.
        """
        self.product_id = product_id
        self.doc = None

    async def init(self, total: int):
        """
        Initialize or reset the progress doc.

        Args:
            total: Total files count.
        """
        now = datetime.now(timezone.utc)
        existing = await AnalyzeProductProfileProgress.find_one(
            AnalyzeProductProfileProgress.product_id == self.product_id
        )
        if existing:
            existing.total_files = total
            existing.processed_files = 0
            existing.updated_at = now
            self.doc = existing
        else:
            self.doc = AnalyzeProductProfileProgress(
                product_id=self.product_id,
                total_files=total,
                processed_files=0,
                updated_at=now,
            )
        await self.doc.save()
        logger.info("Initialized progress for %s: %d files", self.product_id, total)

    async def increment(self):
        """
        Increment processed_files by one.
        """
        if not self.doc:
            raise HTTPException(500, "Progress not initialized.")
        self.doc.processed_files += 1
        self.doc.updated_at = datetime.now(timezone.utc)
        await self.doc.save()

    async def complete(self):
        """
        Mark progress complete (processed_files == total_files).
        """
        if not self.doc:
            return
        self.doc.processed_files = self.doc.total_files
        self.doc.updated_at = datetime.now(timezone.utc)
        await self.doc.save()
        logger.info("Progress complete for %s", self.product_id)


class AnalyzeProductProfileService:
    """
    Coordinates the analysis flow under a Redis lock to prevent races.
    """

    def __init__(self, product_id: str):
        """
        Args:
            product_id: Identifier for the product to analyze.
        """
        self.product_id = product_id
        self.lock = redis_client.lock(f"analyze_lock:{product_id}", timeout=60)
        self.client = get_openai_client()
        self.progress = ProgressTracker(product_id)

    async def run(self):
        """
        Perform analysis steps:
          1. Acquire lock
          2. Fetch docs and init progress
          3. Upload files and track progress
          4. Setup and invoke assistant
          5. Parse and persist ProductProfile
          6. Finalize progress and release lock
        """
        if not await self.lock.acquire(blocking=False):
            logger.warning("Analysis already running for %s", self.product_id)
            return
        try:
            docs = await get_product_profile_documents(self.product_id)
            await self.progress.init(len(docs) + 1)  # +1 for the final completion step

            uploader = FileUploader(self.client)
            file_ids = []
            for doc in docs:
                try:
                    fid = await uploader.upload(doc)
                except Exception as e:
                    logger.error("Upload failed for %s: %s", doc.file_name, e)
                    raise HTTPException(502, f"Upload failed for {doc.file_name}")
                file_ids.append(fid)
                await self.progress.increment()
                logger.info("Uploaded %s as %s", doc.file_name, fid)
            await uploader.close()

            schema = ProfileSchema.model_json_schema(by_alias=True)
            assistant = AssistantManager(self.client)
            await assistant.setup(schema)
            await assistant.submit(file_ids)
            response = await assistant.run()
            profile_data = parse_openai_json(response)
            await assistant.cleanup(file_ids)

            # Persist profile
            await ProductProfile.find(
                ProductProfile.product_id == self.product_id
            ).delete_many()
            await ProductProfile(**{
                **profile_data,
                "product_id": self.product_id,
            }).save()

            await self.progress.complete()
            logger.success("Saved product profile for %s", self.product_id)
        except Exception as exc:
            logger.error("Error analyzing %s: %s", self.product_id, exc)
            raise
        finally:
            try:
                await self.lock.release()
            except Exception:
                logger.warning("Failed to release lock for %s", self.product_id)
