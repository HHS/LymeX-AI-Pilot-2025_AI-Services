"""
1. Single assistant instance with 12 tools (analytical, comparison, clinical …)
2. `_generic_extract()` drives the loop and validation.
3. Thin wrappers list which files to pass and which schema / attr to use.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
import httpx
import asyncio
import io
import re
from loguru import logger

from src.infrastructure.openai import get_openai_client_sync
from src.infrastructure.redis import redis_client

from src.modules.performance_testing.storage import (
    get_performance_testing_documents,  # ← new
)

from src.utils.parse_openai_json import parse_openai_json
from src.modules.performance_testing.plan_model import PerformanceTestPlan
from src.modules.performance_testing.performance_test_planner import create_plan

from src.modules.performance_testing.model import (
    PerformanceTesting,
    AnalyzePerformanceTestingProgress,
)
from src.modules.performance_testing.schema import (
    AnalyticalStudy,
    ComparisonStudy,
    ClinicalStudy,
    AnimalTesting,
    EMCSafety,
    WirelessCoexistence,
    SoftwarePerformance,
    Interoperability,
    Biocompatibility,
    SterilityValidation,
    ShelfLife,
    CyberSecurity,
)


# ─────── Progress helper ────────────────────────────────────────
class AnalyzePTProgress:
    """Thin wrapper around the AnalyzePerformanceTestingProgress document."""

    def __init__(self) -> None:
        self.doc: AnalyzePerformanceTestingProgress | None = None

    async def init(self, product_id: str, total_sections: int) -> None:
        now = datetime.now(timezone.utc)
        existing = await AnalyzePerformanceTestingProgress.find_one(
            AnalyzePerformanceTestingProgress.product_id == product_id
        )
        if existing:
            existing.total_sections = total_sections
            # existing.processed_files  = 0
            existing.updated_at = now
            self.doc = existing
        else:
            self.doc = AnalyzePerformanceTestingProgress(
                product_id=product_id,
                total_sections=total_sections,
                # processed_files= 0,
                updated_at=now,
            )
        await self.doc.save()

    async def tick(self, n: int = 1) -> None:
        if not self.doc:
            return
        self.doc.processed_files += n
        self.doc.updated_at = datetime.now(timezone.utc)
        await self.doc.save()

    async def done(self) -> None:
        if not self.doc:
            return
        self.doc.processed_sections = self.doc.total_sections
        self.doc.updated_at = datetime.now(timezone.utc)
        await self.doc.save()

    async def err(self) -> None:
        if not self.doc:
            return
        self.doc.processed_sections = -1
        self.doc.updated_at = datetime.now(timezone.utc)
        await self.doc.save()
        logger.error("Progress marked as errored for {}", self.doc.product_id)


# ───────── helpers ───────────────────────────────────────────
async def _get_or_create(pid: str) -> PerformanceTesting:
    doc = await PerformanceTesting.find_one({"product_id": pid})
    if not doc:
        doc = PerformanceTesting(product_id=pid)
        await doc.insert()
    return doc


async def _maybe_upload_local_file(client, ids: List[str]) -> List[str]:
    if ids != ["local"]:
        return ids
    pdf = Path("dev_assets/perf_testing_dummy.pdf")
    with pdf.open("rb") as fh:
        fid = client.files.create(file=fh, purpose="assistants").id
    logger.info("🔄 Using local PDF {} → {}", pdf.name, fid)
    return [fid]


async def _upload_via_url(client, url: str, filename: str) -> str:
    """
    Download a doc from MinIO (via pre-signed URL) and push it to
    OpenAI's /files endpoint. Returns the new file-ID.
    """

    async with httpx.AsyncClient() as http:
        r = await http.get(url, timeout=60)
        r.raise_for_status()
    bio = io.BytesIO(r.content)
    bio.name = filename  # important so GPT “sees” the name
    uploaded = client.files.create(file=bio, purpose="assistants")
    return uploaded.id


def _robust_json(txt: str) -> dict:
    """
    1. plain json.loads()
    2. strip code-fences / pick first balanced {...}
    3. final fallback: parse_openai_json()  (removes trailing text, etc.)
    """
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        # common pattern: ```json … ```
        if txt.startswith("```"):
            txt = txt.strip("` \n")
            if txt.lower().startswith("json"):
                txt = txt[4:].lstrip()  # drop leading “json”
        # grab the first {...} block
        m = re.search(r"\{.*\}", txt, flags=re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass  # fall through
        # last resort – very tolerant but slower
        return parse_openai_json(txt)


# ───────── assistant ────────────────────────────────────────
async def _assistant_id(client) -> str:
    tools = [
        {"type": "file_search"},
    ]
    mapping = {
        "submit_analytical_section": AnalyticalStudy,
        "submit_comparison_section": ComparisonStudy,
        "submit_clinical_section": ClinicalStudy,
        "submit_animal_section": AnimalTesting,
        "submit_emc_section": EMCSafety,
        "submit_wireless_section": WirelessCoexistence,
        "submit_software_section": SoftwarePerformance,
        "submit_interop_section": Interoperability,
        "submit_biocomp_section": Biocompatibility,
        "submit_sterility_section": SterilityValidation,
        "submit_shelf_life_section": ShelfLife,
        "submit_cyber_section": CyberSecurity,
    }
    for name, cls in mapping.items():
        tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": f"Return {cls.__name__} JSON.",
                "parameters": cls.model_json_schema(by_alias=True),
            },
        })

    assistant = client.beta.assistants.create(
        name="Performance‑Testing extractor",
        model="gpt-4o",
        instructions=(
            "You are an FDA performance-testing analyst. For each question‑naire "
            "section respond ONLY by calling the matching function tool named "
            "'submit_*_section'. If no data for a section, set performed=false "
            "or return key_results='not available'. Never reply with free text."
        ),
        tools=tools,
    )
    return assistant.id, mapping


# ───────── generic extractor ─────────────────────────────────
async def _generic_extract(
    client,
    assistant_id: str,
    product_id: str,
    attachments: List[str],
    tool_name: str,
    schema_cls,
    attr_name: str,
    prompt: str,
    progress: AnalyzePTProgress | None = None,
):
    attachments = await _maybe_upload_local_file(client, attachments)
    if not attachments:
        logger.warning("No files for {}", tool_name)
        return

    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt,
        attachments=[
            {"file_id": fid, "tools": [{"type": "file_search"}]} for fid in attachments
        ],
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=assistant_id
    )
    record: dict | None = None

    for _ in range(120):
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run.status == "requires_action":
            outs = []
            calls = run.required_action.submit_tool_outputs.tool_calls
            for tc in calls:
                if tc.type == "function" and tc.function.name == tool_name:
                    if record is None:
                        arg = tc.function.arguments
                        record = _robust_json(arg) if isinstance(arg, str) else arg
                    outs.append({"tool_call_id": tc.id, "output": "received"})
                elif tc.type == "file_search":
                    outs.append({
                        "tool_call_id": tc.id,
                        "output": {"data": [{"page": 1, "snippet": ""}]},
                    })
            client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id, run_id=run.id, tool_outputs=outs
            )
        elif run.status in ("completed", "failed", "cancelled", "expired"):
            break
        await asyncio.sleep(5)

    # fallback plain‑text JSON
    if record is None:
        for msg in client.beta.threads.messages.list(thread_id=thread.id).data:
            if msg.role == "assistant":
                try:
                    record = json.loads(msg.content[0].text.value)
                    break
                except Exception:
                    continue
    if record is None:
        logger.warning("{}: no JSON returned", tool_name)
        return

    # key normalisation
    attachments = record.pop("attachments", None)
    if attachments:  # only if not None / not empty
        record["attachment_ids"] = [a.get("id") for a in attachments if a]

    pages = record.pop("pages", None)
    if pages:
        record["page_refs"] = [p.get("page") for p in pages if p]

    try:
        obj = schema_cls.parse_obj(record)
        logger.debug("🔍 {} JSON:\n{}", tool_name, json.dumps(record, indent=2))
    except Exception as exc:
        logger.warning("{} validation failed: {}", tool_name, exc)
        return

    doc = await _get_or_create(product_id)
    # getattr(doc, attr_name).append(obj)

    slot = getattr(doc, attr_name)
    if isinstance(slot, list):
        slot.append(obj)
    else:
        setattr(doc, attr_name, obj)

    await doc.save()
    logger.info("✅ Saved {} section for {}", tool_name, product_id)

    if progress:  # tick AFTER successful save
        await progress.tick()


# ───────── thin wrappers for each questionnaire section ──────
async def _run_all_sections(client, aid, mapping, pid, atts):
    prompts = {
        "submit_analytical_section": "Extract analytical-performance data. Populate these fields when present:\n"
        "• pro  duct_name • product_identifier • protocol_id • objective • "
        "specimen_description • specimen_collection • samples_replicates_sites • "
        "positive_controls • negative_controls • calibration_requirements • "
        "assay_steps • data_analysis_plan • statistical_analysis_plan • "
        "acceptance_criteria • consensus_standards • deviations • discussion • "
        "conclusion\n"
        "Return them via the function tool. Use 'not available' for any field you "
        "cannot populate.",
        "submit_comparison_section": "Extract method/matrix comparison study data.",
        "submit_clinical_section": "Extract clinical-performance study data.",
        "submit_animal_section": "Extract GLP animal testing data.",
        "submit_emc_section": "Extract EMC / electrical-safety data.",
        "submit_wireless_section": "Extract wireless-coexistence data.",
        "submit_software_section": "Extract software performance data.",
        "submit_interop_section": "Extract interoperability data.",
        "submit_biocomp_section": "Extract biocompatibility data.",
        "submit_sterility_section": "Extract sterility validation data.",
        "submit_shelf_life_section": "Extract shelf-life / aging data.",
        "submit_cyber_section": "Extract cyber-security data.",
    }

    attr_map = {
        "AnalyticalStudy": "analytical",
        "ComparisonStudy": "comparison",
        "ClinicalStudy": "clinical",
        "AnimalTesting": "animal_testing",  # single object
        "EMCSafety": "emc_safety",  # single object
        "WirelessCoexistence": "wireless",  # single object
        "SoftwarePerformance": "software",
        "Interoperability": "interoperability",
        "Biocompatibility": "biocompatibility",
        "SterilityValidation": "sterility",
        "ShelfLife": "shelf_life",
        "CyberSecurity": "cybersecurity",
    }

    for tool, cls in mapping.items():
        # attr = cls.__name__.replace("Study", "").replace("Validation", "").lower()
        attr = attr_map[cls.__name__]
        attr = attr if attr != "shelflife" else "shelf_life"
        await _generic_extract(client, aid, pid, atts, tool, cls, attr, prompts[tool])


# ───── helper used to map tool-names → top-level “section keys” ─────
def _section_key(tool_name: str) -> str:
    """
    "submit_analytical_section"  →  "analytical"
    "submit_emc_section"         →  "emc_safety"
    """
    return tool_name.removeprefix("submit_").removesuffix("_section")


# ───────── public entry point ───────────────────────────────
async def analyze_performance_testing(
    product_id: str,
    attachment_ids: Optional[List[str]] = None,
) -> int:
    lock = redis_client.lock(f"pt_analyze_lock:{product_id}", timeout=60)
    if not await lock.acquire(blocking=False):
        logger.warning("Analysis already running for {}", product_id)
        return

    progress = AnalyzePTProgress()

    num_files = -1

    try:
        # ▲ 1) read plan (may be None)
        plan_doc = await PerformanceTestPlan.find_one({"product_id": product_id})
        if plan_doc is None:
            await create_plan(product_id)  # generate test plan on the fly
            plan_doc = await PerformanceTestPlan.find_one({"product_id": product_id})
            # print("📝 NEW test‑plan:\n", plan_doc.model_dump_json(indent=2))

        required_tests = plan_doc.required_tests if plan_doc else None

        # client = get_openai_client_sync()
        # aid, full_mapping = await _assistant_id(client)

        # pull doc list from MinIO if caller didn’t hand us explicit IDs
        if not attachment_ids:
            docs = await get_performance_testing_documents(product_id)

            # Return None cleanly when no files are present
            if not docs:  # len(docs) == 0
                logger.warning(
                    f"No performance-testing documents found for {product_id}; "
                    "AI processing can’t be done."
                )
                return None  # signals None to the caller

            client = get_openai_client_sync()  # need client early
            uploads = []
            num_files = len(docs)  # pass the number of documents
            for d in docs:
                try:
                    fid = await _upload_via_url(client, d.url, d.file_name)
                    uploads.append(fid)
                except Exception as exc:
                    logger.warning("⚠️  upload failed for %s: %s", d.file_name, exc)
            attachment_ids = uploads
            logger.info(" %d PDFs uploaded for %s", len(uploads), product_id)
        else:
            num_files = len(
                attachment_ids
            )  # pass the number of documents based on their attachment_ids
            client = get_openai_client_sync()  # unchanged path

        aid, full_mapping = await _assistant_id(client)

        # ▲ 2) filter mapping to sections present in the plan
        if required_tests is not None:
            mapping = {
                k: v
                for k, v in full_mapping.items()
                if required_tests.get(_section_key(k))
            }
        else:
            mapping = full_mapping  # legacy: run all

        # initialise progress BEFORE starting extraction
        await progress.init(product_id, total_sections=len(mapping))

        await PerformanceTesting.find(
            PerformanceTesting.product_id == product_id
        ).delete_many()
        await _run_all_sections(client, aid, mapping, product_id, attachment_ids)

        await progress.done()  # mark 100 %
    except Exception as exc:
        logger.error("Performance testing analysis failed for %s: %s", product_id, exc)
        await progress.err()
    finally:
        await lock.release()

    return num_files
