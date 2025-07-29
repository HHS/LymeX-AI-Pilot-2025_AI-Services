"""
End-to-end analysis entry-point.
"""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

import httpx
from fastapi import HTTPException
from loguru import logger

from src.infrastructure.redis import redis_client
from src.services.openai.extract_files_data import extract_files_data  # existing helper
from src.utils.prompt import model_to_schema

from src.modules.product_profile.model import ProductProfile
from src.modules.product_profile.storage import get_product_profile_documents
from .model import ClaimBuilder
from .analyze_progress import AnalyzeProgress
from src.modules.competitive_analysis.model import CompetitiveAnalysis


# --------------------------------------------------------------------- #
# helper utilities
# --------------------------------------------------------------------- #


async def _download_to_tmp(url: str, suffix: str = ".pdf") -> Path:
    """Download *url* to a NamedTemporaryFile and return its Path."""
    async with httpx.AsyncClient() as http:
        resp = await http.get(url)
        resp.raise_for_status()

    tmp_fd, tmp_name = tempfile.mkstemp(suffix=suffix)
    Path(tmp_name).write_bytes(resp.content)
    return Path(tmp_name)


def _build_system_prompt(model_cls: type[ClaimBuilder]) -> str:
    """Generate an instruction block containing the JSON schema."""
    schema = model_to_schema(model_cls)
    return f"""
You are an expert at extracting structured information from regulatory and product documentation for medical devices.

Your task:
- Read and analyze all uploaded PDF documents.
- Extract all relevant information and return a JSON object that exactly matches the following ClaimBuilder schema.
- Only include fields present in the schema, matching their types and structure.

# ClaimBuilder JSON Schema

{schema}

# Output
Return only the final JSON object matching the schema above, ready for deserialization into the ClaimBuilder model.

Strictly output valid JSON.
""".strip()


# --------------------------------------------------------------------- #
# main orchestration
# --------------------------------------------------------------------- #


async def analyze_claim_builder(product_id: str) -> None:
    """
    Background task entry that:
      • grabs IFU text,
      • gathers supporting PDFs,
      • calls OpenAI once (JSON-mode),
      • saves/overwrites the ClaimBuilder document.
    """

    lock_key = f"NOIS2:Background:AnalyzeClaimBuilder:AnalyzeLock:{product_id}"
    lock = redis_client.lock(lock_key, timeout=150)

    # --------------------------------- progress doc --------------------------------- #
    progress = AnalyzeProgress()
    await progress.init(product_id=product_id, total_files=1)

    if not await lock.acquire(blocking=False):
        logger.info("[%s] another job in progress – skipping", product_id)
        return

    try:
        # --------------------------------- gather data ---------------------------------- #
        sleep_time = 5
        max_retries = 20  # 100 seconds max
        for _ in range(max_retries):
            profile = await ProductProfile.find_one(
                ProductProfile.product_id == product_id
            )
            if profile:
                break
            logger.warning("⏳  Waiting for Product-Profile to be available...")
            await asyncio.sleep(sleep_time)
        else:
            raise HTTPException(404, "Product-Profile not found for this product")
        if profile is None:
            raise HTTPException(404, f"No ProductProfile found for '{product_id}'")

        ifu_text: str | None = getattr(profile, "instructions_for_use", None)
        if not ifu_text:
            raise HTTPException(
                422,
                "ProductProfile.instructions_for_use is empty - cannot analyse IFU",
            )

        docs = await get_product_profile_documents(product_id)

        # Prefer local cached path if storage layer provides it; otherwise download
        file_paths: list[Path] = []
        for d in docs:
            if getattr(d, "path", None):
                file_paths.append(Path(d.path))
            else:
                file_paths.append(await _download_to_tmp(d.url))

        # --------------------------------- OpenAI call ---------------------------------- #
        system_prompt = _build_system_prompt(ClaimBuilder)
        """user_msg = (
            f"Below is the full IFU text for product **{product_id}**:\n\n{ifu_text}\n\n"
            "Please analyse the IFU and all attached PDFs."
        )
        """
        user_msg = (
            f"You are reviewing the following Instructions-for-Use (IFU) for "
            f"product **{product_id}**:\n\n"
            "```text\n"
            f"{ifu_text}\n"
            "```\n\n"
            "• Identify every issue (missing element, clarity, refactoring). "
            "  **Severity must be exactly `LOW`, `MEDIUM`, or `CRITICAL`.** "  # to prevent wrong data
            "• Detect conflicts inside the IFU and against the PDFs if relevant. "
            "• Detect any phrase conflicts in refrence to regulatory standards."
            "Return a **single** JSON object that exactly matches the "
            "`ClaimBuilder` schema provided earlier.  No extra keys, "
            "no markdown, valid JSON only."
        )

        result: ClaimBuilder = await extract_files_data(
            file_paths=file_paths,
            system_instruction=system_prompt,
            user_question=user_msg,
            model_class=ClaimBuilder,
        )

        # --------------------------------- DB insert ------------------------------------ #
        # clean old doc then insert the new one so _id stays stable
        await ClaimBuilder.find(ClaimBuilder.product_id == product_id).delete_many()

        result.product_id = product_id
        result.is_user_input = False  # mark as AI analysis complete

        # get Competetive analysis
        comp_analysis = await CompetitiveAnalysis.find_one({"product_id": product_id})
        # if Competetive analysis available then assign indications for use statement else skip
        if comp_analysis and getattr(comp_analysis, "indications_for_use_statement", None):
            result.draft[0].content = comp_analysis.indications_for_use_statement
        else:
            logger.info("Competitive Analysis data not available for  %s", product_id)

        await result.save()

        await progress.complete()
        logger.info("ClaimBuilder saved for %s", product_id)

    except Exception as exc:
        logger.error("ClaimBuilder analysis failed for %s: %s", product_id, exc)
        await progress.err()
        raise
    finally:
        try:
            await lock.release()
        except Exception:
            pass
