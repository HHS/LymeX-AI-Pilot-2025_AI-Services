"""
Performance-Test Planner
------------------------

1. Should be triggered when a *ProductProfile* is finalised (or re-saved).
2. Reads the Product-Profile PDF directly (via file-search).
3. Returns a machine–readable checklist of required *individual* performance
   tests (see const.TEST_CATALOGUE).
4. Persists the checklist in `performance_test_plan` Mongo collection.

Public API:
    await create_plan(product_id: str, profile_pdf_id: str)
"""

from __future__ import annotations

import asyncio, json
from datetime import datetime
from typing import Dict, List

from loguru import logger
from fastapi import HTTPException

from src.infrastructure.openai import get_openai_client
from src.modules.performance_testing.const import TEST_CATALOGUE
from src.modules.performance_testing.plan_model import PerformanceTestPlan
from src.modules.product_profile.model import ProductProfile  # for rule engine

# we will reuse the storage layer that already exists for Product-Profile
from src.modules.product_profile.storage  import get_product_profile_documents
from src.utils.upload_helpers import upload_via_url

# ─────────────────────────────────────────────────────────────
# 1.  Helper: simple rule-engine (cheap heuristics first)
# ─────────────────────────────────────────────────────────────
def _rule_engine(profile: ProductProfile) -> Dict[str, List[str]]:
    """Return a *minimal* starter checklist derived from obvious flags."""

    out: Dict[str, List[str]] = {}

    def add(section: str, *codes: str):
        out.setdefault(section, []).extend(codes)
    
    add("analytical", "precision", "linearity", "sensitivity")
    add("clinical", "clin_sens_spec")
    if getattr(profile, "contains_software", False):
        add("software", *TEST_CATALOGUE["software"].keys())
        add("cybersecurity", "security_rm_report", "sbom", "threat_model")
    if getattr(profile, "wireless_capability", False):
        add("emc_safety", "iec_60601_1_2")
        add("wireless", "coexistence")
    # …extend with more rules…

    return out


# ─────────────────────────────────────────────────────────────
# 2.  Helper: poll assistant until function JSON is returned
# ─────────────────────────────────────────────────────────────
async def _poll_function_json(client, thread_id: str, run_id: str,
                              function_name: str) -> dict:
    """Wait until the assistant calls *function_name* and return its arguments."""
    for _ in range(120):
        run = client.beta.threads.runs.retrieve(thread_id=thread_id,
                                                run_id=run_id)

        if run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls

            outs: list[dict] = []
            fn_args: dict | None = None

            for tc in tool_calls:
                if tc.type == "function" and tc.function.name == function_name:
                    # --- capture the arguments we actually care about
                    raw = tc.function.arguments
                    fn_args = json.loads(raw) if isinstance(raw, str) else raw
                    outs.append({"tool_call_id": tc.id, "output": "received"})

                elif tc.type == "file_search":
                    # --- return an empty stub so the assistant knows the call succeeded
                    outs.append({
                        "tool_call_id": tc.id,
                        "output": {"data": [{"page": 1, "snippet": ""}]},
                    })

            # >>> Submit *all* the collected outputs in one shot
            if outs:
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id, run_id=run.id, tool_outputs=outs
                )

            # Only exit the polling loop after we have answered **every**
            # outstanding tool call *and* captured the arguments we need
            if fn_args is not None:
                return fn_args

        elif run.status in ("completed", "failed", "cancelled", "expired"):
            break

        await asyncio.sleep(3)

    raise HTTPException(502, f"Assistant never returned {function_name}")


# ─────────────────────────────────────────────────────────────
# 3.  Public entry point
# ─────────────────────────────────────────────────────────────
async def create_plan(product_id: str, profile_pdf_ids: list[str] | None = None,) -> None:
    """Analyse the Product-Profile PDF + rule engine → store PerformanceTestPlan.

    1. If `profile_pdf_ids` are supplied (fast-path from UI) - use them.
    2. Otherwise pull *all* Product-Profile PDFs from MinIO, upload to
       OpenAI, and use those uploads.
        
    """

    logger.info("🛠  Generating test-plan for {}", product_id)

    # ── Fetch profile for rule-engine (if you keep rules) ──
    profile = await ProductProfile.find_one({"product_id": product_id})
    rule_tests = _rule_engine(profile) if profile else {}

    # ── Build assistant dynamically from TEST_CATALOGUE ────
    client = get_openai_client()

    assistant = client.beta.assistants.create(
        name="Performance Test Planner",
        model="gpt-4o-mini",
        instructions=(
             "You are an FDA regulatory strategist.  ALWAYS respond by calling the "
        "function **return_test_plan** with *one* argument named "
        "`required_tests` that maps section keys to arrays of canonical test "
        "codes.  Optionally include a `rationale` string.  Do **not** add any "
        "extra keys or free-text answers.\n\n"
        "Allowed section keys and test codes:\n"
        + json.dumps(TEST_CATALOGUE, indent=2)
        ),
        tools=[
            {"type": "file_search"},
            {"type": "function", "function": {
                "name": "return_test_plan",
                "description": "Return required performance tests.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "required_tests": {
                            "type": "object",
                            "additionalProperties": {
                                "type": "array", "items": {"type": "string"}
                            }
                        },
                        "rationale": {"type": "string"}
                    },
                    "required": ["required_tests"]
                },
            }},
        ],
    )

    # ── 1)  Ensure we have OpenAI file-IDs for **all** profile PDFs
    if profile_pdf_ids is None:
        docs = await get_product_profile_documents(product_id)
        uploads: list[str] = []
        for d in docs:
            try:
                fid = await upload_via_url(client, d.url, d.file_name)
                uploads.append(fid)
            except Exception as exc:
                logger.warning("PDF upload failed for {}: {}", d.file_name, exc)
        profile_pdf_ids = uploads

    if not profile_pdf_ids:
        raise HTTPException(404, "No Product-Profile PDFs found for this product")

    logger.info("⬆️  {} profile PDFs available for planning", len(profile_pdf_ids))

    # ── Kick off assistant with the Product-Profile PDF ────
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Which *individual* performance tests are mandatory?",
        attachments=[
                    {"file_id": fid,
                      "tools":[{"type":"file_search"}]}
                    for fid in profile_pdf_ids#[:10]  
                    ],
    )

    run = client.beta.threads.runs.create(thread_id=thread.id,
                                          assistant_id=assistant.id)

    llm_out = await _poll_function_json(client, thread.id, run.id,
                                        "return_test_plan")
    # debugging
    logger.debug("🔍 Raw planner output:\n{}",
             json.dumps(llm_out, indent=2, ensure_ascii=False))
    
    llm_tests: Dict[str, List[str]] = llm_out["required_tests"]
    rationale: str | None = llm_out.get("rationale")

    # ── Merge rule-engine & LLM (union) ─────────────────────
    merged: Dict[str, List[str]] = {}
    for sec, tests in TEST_CATALOGUE.items():
        merged[sec] = sorted(
            set(rule_tests.get(sec, [])) | set(llm_tests.get(sec, []))
        )

    # ── Save / replace plan in DB ───────────────────────────
    """await PerformanceTestPlan.find_one(
        {"product_id": product_id}).delete()  # idempotent"""
    existing_doc = await PerformanceTestPlan.find_one({"product_id": product_id})
    if existing_doc:                       # None if no previous plan
        await existing_doc.delete()        # async method on the document
    
    await PerformanceTestPlan(
        product_id=product_id,
        required_tests=merged,
        rationale=rationale,
        updated_at=datetime.utcnow()
    ).insert()

    logger.success("🎯 Test-plan stored with {} total tests",
                   sum(len(v) for v in merged.values()))
