"""
1. Single assistant instance with 12 tools (analytical, comparison, clinical …)
2. `_generic_extract()` drives the loop and validation.
3. Thin wrappers list which files to pass and which schema / attr to use.
"""

from __future__ import annotations

import asyncio, json
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import HTTPException
from loguru import logger

from src.infrastructure.openai import get_openai_client
from src.infrastructure.redis import redis_client
from src.modules.performance_testing.model import PerformanceTestingDocument
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

# ───────── helpers ───────────────────────────────────────────
async def _get_or_create(pid: str) -> PerformanceTestingDocument:
    doc = await PerformanceTestingDocument.find_one({"product_id": pid})
    if not doc:
        doc = PerformanceTestingDocument(product_id=pid)
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
        attachments=[{"file_id": fid, "tools": [{"type": "file_search"}]} for fid in attachments],
    )

    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)
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
                        record = json.loads(arg) if isinstance(arg, str) else arg
                    outs.append({"tool_call_id": tc.id, "output": "received"})
                elif tc.type == "file_search":
                    outs.append({"tool_call_id": tc.id, "output": {"data": [{"page": 1, "snippet": ""}]}})
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
    if "attachments" in record:
        record["attachment_ids"] = [a.get("id") for a in record.pop("attachments")]
    if "pages" in record:
        record["page_refs"] = [p.get("page") for p in record.pop("pages")]

    try:
        obj = schema_cls.parse_obj(record)
        logger.debug("🔍 {} JSON:\n{}", tool_name, json.dumps(record, indent=2))
    except Exception as exc:
        logger.warning("{} validation failed: {}", tool_name, exc)
        return

    doc = await _get_or_create(product_id)
    #getattr(doc, attr_name).append(obj)
    
    slot = getattr(doc, attr_name)
    if isinstance(slot, list):
        slot.append(obj)
    else:
        setattr(doc, attr_name, obj)
    
    await doc.save()
    logger.info("✅ Saved {} section for {}", tool_name, product_id)

# ───────── thin wrappers for each questionnaire section ──────
async def _run_all_sections(client, aid, mapping, pid, atts):
    prompts = {
        "submit_analytical_section": "Extract analytical-performance data. Populate these fields when present:\n"
        "• product_name • product_identifier • protocol_id • objective • "
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
    "AnalyticalStudy":      "analytical",
    "ComparisonStudy":      "comparison",
    "ClinicalStudy":        "clinical",
    "AnimalTesting":        "animal_testing",   # single object
    "EMCSafety":            "emc_safety",       # single object
    "WirelessCoexistence":  "wireless",         # single object
    "SoftwarePerformance":  "software",
    "Interoperability":     "interoperability",
    "Biocompatibility":     "biocompatibility",
    "SterilityValidation":  "sterility",
    "ShelfLife":            "shelf_life",
    "CyberSecurity":        "cybersecurity",
    }

    for tool, cls in mapping.items():
        #attr = cls.__name__.replace("Study", "").replace("Validation", "").lower()
        attr = attr_map[cls.__name__]
        attr = attr if attr != "shelflife" else "shelf_life"
        await _generic_extract(
            client, aid, pid, atts, tool, cls, attr, prompts[tool]
        )

# ───────── public entry point ───────────────────────────────
async def analyze_performance_testing(product_id: str, attachment_ids: List[str]):
    lock = redis_client.lock(f"pt_analyze_lock:{product_id}", timeout=60)
    if not await lock.acquire(blocking=False):
        logger.warning("Analysis already running for {}", product_id)
        return
    try:
        client = get_openai_client()
        aid, mapping = await _assistant_id(client)
        await _run_all_sections(client, aid, mapping, product_id, attachment_ids)
    finally:
        await lock.release()
