from __future__ import annotations

import asyncio
from datetime import datetime
from typing import List
from io import BytesIO
from pathlib import Path

import json, pprint #----------

from loguru import logger
from fastapi import HTTPException

from src.infrastructure.openai import get_openai_client
from src.infrastructure.redis import redis_client
from src.modules.performance_testing.model import PerformanceTestingDocument
from src.modules.performance_testing.schema import AnalyticalStudy


async def _get_or_create(product_id: str) -> PerformanceTestingDocument:
    doc = await PerformanceTestingDocument.find_one(
        {"product_id": product_id}
    )
    if doc is None:
        doc = PerformanceTestingDocument(product_id=product_id)
        await doc.insert()
    return doc


async def _patch_section(doc: PerformanceTestingDocument, section_name: str, payload):
    setattr(doc, section_name, payload)
    doc.updated_at = datetime.utcnow()
    await doc.save()

# create an assistant pre‑configured for Analytical extraction
async def _create_analytical_assistant(client) -> str:
    function_schema = AnalyticalStudy.model_json_schema(by_alias=True)

    assistant = client.beta.assistants.create(
        instructions=(
            "You are an FDA performance-testing analyst. Parse any attached "
            "analytical-performance protocols or reports and ALWAYS respond by "
            "calling the function `submit_analytical_section`. "
            "If no analytical data is found, call the function with "
            "performed=false and key_results='not available'. "
            "Do not output plain text." #---------------------------------------------------------------
        ),
        model="gpt-4o",  # changed to gpt-40 to support file search
        tools=[
            {"type": "file_search"},
            {"type": "function", "function": {
                "name": "submit_analytical_section",
                "description": "Return analytical‑performance results.",
                "parameters": function_schema,
            }},
        ],
    )
    return assistant.id


# Development helper: allow local PDF when attachment_ids == ["local"] for testing and debugging
async def _maybe_upload_local_file(client, attachment_ids: List[str]) -> List[str]:
    if attachment_ids != ["local"]:
        return attachment_ids

    dev_pdf = Path("C:/Users/yishu/Downloads/EMC dummy report.pdf")
    if not dev_pdf.exists():
        raise FileNotFoundError(dev_pdf)
    with dev_pdf.open("rb") as f:
        uploaded = client.files.create(file=f, purpose="assistants")
    logger.info(f"🔄 Using local PDF {dev_pdf.name} → {uploaded.id}")
    return [uploaded.id]


# Extraction routine for Analytical Performance
async def _extract_analytical(client, assistant_id: str, product_id: str, attachment_ids: List[str]):
    attachment_ids = await _maybe_upload_local_file(client, attachment_ids)
    if not attachment_ids:
        logger.warning("No attachments for analytical extraction; skipping")
        return

    # Map assistant file‑search IDs (one‑to‑one mapping in this simplified flow)
    thread = client.beta.threads.create()

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=(
            "Analyse the attached analytical‑performance files and return the "
            "AnalyticalStudy JSON via the function tool."
        ),
        attachments=[{"file_id": fid, "tools": [{"type": "file_search"}]} for fid in attachment_ids],
    )

    
    # Run the assistant and poll for completion --------------------------------------------------------------
    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)

    print(f" run_id: {run.id}") #

    section_json: dict | None = None #

    for _ in range(120):  # up to 10 minutes
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    

        if run.status == "completed":
            break
            
        if run.status == "failed":
            logger.error(f"Assistant run failed: {run.error}")
            raise HTTPException(502, "Assistant failed")
        
        if run.status == "requires_action":
            ra = run.required_action #
            print("    ↳ required_action:", ra.type) #

            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            # only keep first non-empty JSON we receive
            if section_json: #--------------------------
                already_have_json = True
            else:
                already_have_json = False #-------------------

            for tc in tool_calls:
                pprint.pprint(tc.model_dump(), depth=3)
                if tc.type == "function" and tc.function.name == "submit_analytical_section":
                    if section_json is None:            # capture only the first time
                        arg_obj = tc.function.arguments
                        # SDK returns a dict, but older versions return a JSON string
                        if isinstance(arg_obj, str):
                            try:
                                section_json = json.loads(arg_obj)
                            except json.JSONDecodeError as e:
                                print("⚠️  could not decode JSON:", e)
                        else:
                            section_json = arg_obj      # already a dict
                    tool_outputs.append({"tool_call_id": tc.id, "output": "received"})

                elif tc.type == "file_search":
                    tool_outputs.append({
                        "tool_call_id": tc.id,
                        "output": {"data": [{"page": 1, "snippet": ""}]},
                    })

            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs,
            )
        
        elif run.status in ("completed", "failed", "cancelled", "expired"): #
            print("🔚 final status:", run.status) #
            break #

        print(f"Status = {run.status}")

        await asyncio.sleep(5)
        # -------------------------------------------------------------------------------------

    if section_json is None:
        # 🔍 fallback – look for plain-text JSON in assistant messages
        msgs = client.beta.threads.messages.list(thread_id=thread.id)

        for msg in msgs.data:
            if msg.role != "assistant":
                continue
            try:
                # the assistant’s first content part is usually text
                txt = msg.content[0].text.value
                section_json = json.loads(txt)
                break
            except Exception:
                continue
    
    if not section_json:
        logger.warning("Assistant did not return AnalyticalStudy JSON; skipping")
        return

    try:
        section = AnalyticalStudy.parse_obj(section_json)   # validate *this* dict
    except Exception as exc:
        logger.error(f"AnalyticalStudy validation failed: {exc}")
        return

    doc = await _get_or_create(product_id)
    doc.analytical.append(section)
    await doc.save()
    logger.info(f"✅ Analytical section saved for {product_id}")


# public coroutine for all submodules of performance testing
async def analyze_performance_testing(product_id: str, attachment_ids: List[str]):

    lock = redis_client.lock(f"pt_analyze_lock:{product_id}", timeout=60)
    if not await lock.acquire(blocking=False):
        logger.warning(f"Performance‑testing analysis already running for {product_id}")
        return

    try:
        client = get_openai_client()
        assistant_id = await _create_analytical_assistant(client)

        await _extract_analytical(client, assistant_id, product_id, attachment_ids)
        # TODO: replicate for EMC, Clinical, etc.

    finally:
        try:
            await lock.release()
        except Exception:
            pass
