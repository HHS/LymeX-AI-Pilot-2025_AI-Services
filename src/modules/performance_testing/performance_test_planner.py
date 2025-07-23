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

import asyncio
import json
from datetime import datetime
from typing import Dict, List
import re

from loguru import logger
from fastapi import HTTPException

from src.environment import environment
from src.infrastructure.openai import get_openai_client_sync
from src.modules.performance_testing.const import TEST_CATALOGUE
from src.modules.performance_testing.plan_model import PerformanceTestPlan
from src.modules.product_profile.model import ProductProfile  # for rule engine

from src.modules.performance_testing.schema import (
    PerformanceTestCard,
    PerformanceTestingConfidentLevel,
    RiskLevel,
    ModuleStatus,
    PerformanceTestingReference,
    PerformanceTestingAssociatedStandard,
)

# we will reuse the storage layer that already exists for Product-Profile
from src.modules.product_profile.storage import get_product_profile_documents
from src.utils.upload_helpers import upload_via_url
from src.utils.parse_openai_json import parse_openai_json   # tolerant helper

# ───────────────── tolerant JSON loader ────────────────────────
def _robust_json(txt: str) -> dict:
    """
    1. try plain json.loads()
    2. strip code fences / pick first balanced {...}
    3. final fallback: parse_openai_json()  (very forgiving)
    """
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        # common pattern: ```json … ```
        if txt.startswith("```"):
            txt = txt.strip("` \n")
            if txt.lower().startswith("json"):
                txt = txt[4:].lstrip()
        # grab the first {...} block
        m = re.search(r"\{.*\}", txt, flags=re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
        # last resort – very tolerant but slower
        return parse_openai_json(txt)

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
async def _poll_function_json(
    client, thread_id: str, run_id: str, function_name: str
) -> dict:
    """Wait until the assistant calls *function_name* and return its arguments."""
    for _ in range(120):
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)

        if run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls

            outs: list[dict] = []
            fn_args: dict | None = None

            for tc in tool_calls:
                if tc.type == "function" and tc.function.name == function_name:
                    # --- capture the arguments we actually care about
                    #raw = tc.function.arguments
                    #fn_args = json.loads(raw) if isinstance(raw, str) else raw
                    raw = tc.function.arguments
                    fn_args = (
                        _robust_json(raw) if isinstance(raw, str) else raw
                    )
                    outs.append({"tool_call_id": tc.id, "output": "received"})

                elif tc.type == "file_search":
                    # --- return an empty stub so the assistant knows the call succeeded
                    outs.append(
                        {
                            "tool_call_id": tc.id,
                            "output": {"data": [{"page": 1, "snippet": ""}]},
                        }
                    )

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
async def create_plan(
    product_id: str,
    profile_pdf_ids: list[str] | None = None,
) -> None:
    """Analyse the Product-Profile PDF + rule engine → store PerformanceTestPlan.

    1. If `profile_pdf_ids` are supplied (fast-path from UI) - use them.
    2. Otherwise pull *all* Product-Profile PDFs from MinIO, upload to
       OpenAI, and use those uploads.

    """

    logger.info("🛠  Generating test-plan for {}", product_id)

    # ── Fetch profile for rule-engine (if you keep rules) ──
    sleep_time = 5
    max_retries = 20  # 100 seconds max
    for _ in range(max_retries):
        profile = await ProductProfile.find_one({"product_id": product_id})
        if profile:
            break
        logger.warning("⏳  Waiting for Product-Profile to be available...")
        await asyncio.sleep(sleep_time)
    else:
        raise HTTPException(404, "Product-Profile not found for this product")

    rule_tests = _rule_engine(profile)
    
    function_parameters = {
        "type": "object",
        "properties": {
            "tests": {
                "type": "array",
                "minItems": 5,
                "items": {
                    "type": "object",
                    "properties": {
                        "section_key": {"type": "string"},
                        "test_code":   {"type": "string"},
                        "risk_level":  {"type": "string",
                                        "enum": ["Low","Medium","High"]},
                        "ai_confident": {"type": "integer"},
                        "ai_rationale": {"type": "string"},
                        "references": {                     # NEW ▼
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "url":   {"type": "string"},
                                    "description": {"type": "string"},
                                },
                                "required": ["title", "url", "description"]
                            }
                        },
                        "associated_standards": {          # NEW ▼
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "standard_name": {"type": "string"},
                                    "version": {"type": "string"},
                                    "url": {"type": "string"},
                                    "description": {"type": "string"},
                                },
                                "required": ["name", "standard_name","url"]
                            }
                        },
                    },
                    "required": ["section_key", "test_code", "ai_rationale", "references", "associated_standards"]
                }
            },
            "rationale": {"type": "string"}
        },
        "required": ["tests"]
    }
    
    # ── Build assistant dynamically from TEST_CATALOGUE ────
    client = get_openai_client_sync()

    assistant = client.beta.assistants.create(
        name="Performance Test Planner",
        model=environment.openai_model,
        instructions=(
             "You are an FDA regulatory strategist. Always respond by calling the "
            "function **return_test_plan** with a single argument named `tests` - "
            "an *array* of objects. **Each object MUST include**\n"
            "・`section_key`  ・`test_code`  ・`ai_rationale`\n"
            "・**`references` (≥1 item)**  ・**`associated_standards` (≥1 item)**\n"
            "Return at least one authoritative source or standard for every test.\n\n"
             "Allowed combinations are:\n"
            + json.dumps(TEST_CATALOGUE, indent=2)  # keeps catalogue in‑sync
        ),
        tools=[
            {"type": "file_search"},
            {"type": "function", "function": {
                "name": "return_test_plan",
                "description": "Return the flat list of required tests.",
                "parameters": function_parameters,
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
            {"file_id": fid, "tools": [{"type": "file_search"}]}
            for fid in profile_pdf_ids  # [:10]
        ],
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=assistant.id
    )

    llm_out = await _poll_function_json(client, thread.id, run.id, "return_test_plan")
    # debugging
    logger.debug("🔍 Raw planner output:\n{}",
             json.dumps(llm_out, indent=2, ensure_ascii=False))
    
    """llm_tests: Dict[str, List[str]] = {}
    for item in llm_out["tests"]:
        llm_tests.setdefault(item["section_key"], []).append(item["test_code"])"""
    rationale: str | None = llm_out.get("rationale")

    # ── collect extra info per (section, code) ─────────────────────────────
    extras: dict[tuple[str, str], dict] = {}
    llm_tests: Dict[str, List[str]] = {}
    for item in llm_out["tests"]:
        sec, code = item["section_key"], item["test_code"]
        llm_tests.setdefault(sec, []).append(code)
        extras[(sec, code)] = item              # keep full object for later

    # ── Merge rule‑engine & LLM (union) ──────────────────────
    merged: Dict[str, List[str]] = {}
    for section, all_tests in TEST_CATALOGUE.items():
        merged[section] = sorted(
            set(rule_tests.get(section, [])) | set(llm_tests.get(section, []))
        )

    # ── Convert to list[PerformanceTestCard] ─────────────────
    cards: list[PerformanceTestCard] = []
    for section, codes in merged.items():
        for code in codes:

            info = extras.get((section, code), {})

            def _ensure_list(x):
                if not x:
                    return []
                if isinstance(x, list):
                    return x
                # treat "a, b; c" → ["a", "b", "c"]
                clean = re.sub(r"【.*?】", "", str(x))
                return [s.strip() for s in re.split(r"[;,]", clean) if s.strip()]

            # convert raw strings / dicts → Pydantic objects
            ref_objs = [
                PerformanceTestingReference(**r) if isinstance(r, dict)
                else PerformanceTestingReference(title=r)
                for r in _ensure_list(info.get("references"))
            ]

            std_objs = [
                PerformanceTestingAssociatedStandard(**s) if isinstance(s, dict)
                else PerformanceTestingAssociatedStandard(name=s)
                for s in _ensure_list(info.get("associated_standards"))
            ]

            cards.append(
                PerformanceTestCard(
                    # ── mandatory identifiers ────────────────────────
                    section_key   = section,              
                    test_code     = code,

                    # ── descriptive meta‑data ────────────────────────
                    product_id    = product_id,
                    #test_name     = code.replace("_", " ").title(),
                    test_description = TEST_CATALOGUE[section][code],

                    # ── workflow defaults ────────────────────────────
                    status        = ModuleStatus.PENDING,
                    risk_level    = RiskLevel.MEDIUM,
                    ai_confident  = None,
                    confident_level = PerformanceTestingConfidentLevel.LOW,

                    # ── LLM‑supplied meta ─────────────────────────────
                    ai_rationale  = info.get("ai_rationale"),
                    references    = ref_objs or None,
                    associated_standards = std_objs or None,
                )
            )

    # ── Upsert into Mongo ────────────────────────────────────
    if (old := await PerformanceTestPlan.find_one({"product_id": product_id})) :
        #import json, pprint
        logger.warning(
            "Existing plan for %s →\n%s",
            product_id,
            json.dumps(old.model_dump(), indent=2, default=str)
        )
        await old.delete()

    await PerformanceTestPlan(
        product_id=product_id,
        tests=cards,
        rationale=rationale,
        updated_at=datetime.utcnow(),
    ).insert()

    logger.success("Test‑plan stored with {} cards", len(cards))
