from __future__ import annotations
import json
import os
import re
from typing import Optional, Any, List
from loguru import logger

from src.infrastructure.openai import get_openai_client_sync
from src.utils.parse_openai_json import parse_openai_json

from src.modules.performance_testing.const import TEST_CATALOGUE
from src.modules.performance_testing.model import (
    PerformanceTesting,
    PredicateLLMAnalysis,
)
from src.modules.performance_testing.schema import (
    LLMPredicateRow,
    LLMGapFinding,
    LLMPredicateComparisonResult,
)
from src.modules.competitive_analysis.service import get_competitive_analysis


# -------------------- helpers --------------------

# ---------- product name resolver ----------
async def _resolve_product_name(product_id: str) -> str:
   
    try:
        # Local import to avoid import-time hard dependency when running tools
        from src.modules.product_profile.model import ProductProfile
        prof = await ProductProfile.find_one({"product_id": product_id})
        if prof:
            return (
                getattr(prof, "product_trade_name", None)
                or "Not available"
            )
    except Exception:
        pass
    return "Not available"



def _robust_json(txt: str) -> dict:
    try:
        return json.loads(txt)
    except Exception:
        s = txt.strip().replace("```json", "").replace("```", "")
        m = re.search(r"\{.*\}", s, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
        return parse_openai_json(txt)


def _pick_all_competitors(ca_list):
    """Return all non-self-analysis entries; fall back to all if none flagged."""
    non_self = [ca for ca in ca_list if not getattr(ca, "is_self_analysis", False)]
    return non_self or ca_list


def _summarize_pt(pt: PerformanceTesting) -> dict:
    """Keep only the fields relevant for comparison to reduce prompt size."""
    d = pt.model_dump(mode="json")
    keep = {
        "analytical",
        "clinical",
        "emc_safety",
        "software",
        "interoperability",
        "cybersecurity",
        "sterility",
        "shelf_life",
        "biocompatibility",
        "wireless",
        "comparison",
        "overall_risk_level",
    }
    return {k: v for k, v in d.items() if k in keep}


# -------------------- single-competitor run --------------------


async def llm_gaps_and_suggestions_one(
    product_id: str,
    competitor_detail: Any,
    model: str = None,
    product_name: Optional[str] = None,
) -> LLMPredicateComparisonResult:
    """
    Ask OpenAI to detect gaps *and* propose suggestions for THIS competitor only.
    Returns a LLMPredicateComparisonResult (in-memory; not saved).
    """
    logger.info(f"Fetching PerformanceTesting for product_id={product_id}")
    you = await PerformanceTesting.find_one({"product_id": product_id})
    if not you:
        logger.warning(f"No PerformanceTesting found for product_id={product_id}")
        return LLMPredicateComparisonResult(product_id=product_id)
    
    # Ensure we have our own product's display name (required by schema)
    if product_name is None:
        product_name = await _resolve_product_name(product_id)

    details = getattr(competitor_detail, "details", None)
    competitor_name = getattr(details, "product_name", None) if details else None
    competitor_id = (
        str(getattr(competitor_detail, "id", "")) if competitor_detail else None
    )

    pt_ctx = _summarize_pt(you)
    comp_ctx = (
        details.model_dump(mode="json")
        if details and hasattr(details, "model_dump")
        else (details or {})
    )

    logger.debug(
        f"Preparing LLM instructions and payload for product_id={product_id}, competitor_id={competitor_id}"
    )

    instructions = (
        "You are an FDA regulatory analyst. Compare our device's performance evidence with the selected predicate.\n"
        "Return JSON with:\n"
        "  rows: list of {section_key, test_code?, label, your_value?, predicate_value?}\n"
        "  gaps: list of {title, subtitle, suggested_fix, severity in [info,minor,major,critical], section_key, test_code?}\n"
        "Rules:\n"
        "• Do NOT invent numbers; use 'Not available' when missing.\n"
        "• Only create a gap if predicate has evidence or our value is clearly weaker.\n"
        "• Keep suggestions concise (≤2 sentences).\n"
        "• section_key/test_code should align with the catalogue below.\n"
        f"Catalogue:\n{json.dumps(TEST_CATALOGUE, indent=2)}"
    )

    payload = {
        "product_id": product_id,
        "our_performance_testing": pt_ctx,
        "predicate_detail": comp_ctx,
    }

    client = get_openai_client_sync()
    model = model or os.getenv("PT_GAPS_LLM_MODEL", "gpt-4.1-mini")

    logger.info(
        f"Calling OpenAI LLM for product_id={product_id}, competitor_id={competitor_id}, model={model}"
    )

    try:
        resp = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            response_format={"type": "json_object"},
        )
        data = getattr(resp, "output_text", None)
        logger.debug(
            f"LLM response received via responses.create for product_id={product_id}, competitor_id={competitor_id}"
        )
    except Exception as e:
        logger.warning(
            f"LLM responses.create failed: {e}. Falling back to chat.completions.create"
        )
        fallback = os.getenv("PT_GAPS_LLM_MODEL_FALLBACK", "gpt-4o-mini")
        resp = client.chat.completions.create(
            model=fallback,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
                {"role": "system", "content": "Return only a valid JSON object."},
            ],
            temperature=0.2,
        )
        data = resp.choices[0].message.content
        logger.debug(
            f"LLM response received via chat.completions.create for product_id={product_id}, competitor_id={competitor_id}"
        )

    parsed = _robust_json(data or "{}")
    rows = parsed.get("rows") or []
    gaps = parsed.get("gaps") or []

    logger.info(
        f"LLM parsed {len(rows)} rows and {len(gaps)} gaps for product_id={product_id}, competitor_id={competitor_id}"
    )

    # ensure labels exist/are aligned
    for r in rows:
        if not r.get("label"):
            sec, code = r.get("section_key"), r.get("test_code")
            if sec in TEST_CATALOGUE and code in TEST_CATALOGUE[sec]:
                r["label"] = TEST_CATALOGUE[sec][code]
    
    # ensure gap ids and accepted flag exist per schema/UI needs
    for idx, g in enumerate(gaps):
        g.setdefault("id", idx)
        # Accept explicit null; if missing entirely, set to None for UI to toggle later
        if "accepted" not in g:
            g["accepted"] = None

    return LLMPredicateComparisonResult(
        product_id=product_id,
        product_name=product_name,
        competitor_id=competitor_id,
        competitor_name=competitor_name,
        rows=[LLMPredicateRow(**r) for r in rows],
        gaps=[LLMGapFinding(**g) for g in gaps],
        model_used=model,
    )


# -------------------- run for ALL competitors + save --------------------


async def llm_gaps_and_suggestions_all_and_save(
    product_id: str,
    model: str | None = None,
    overwrite: bool = True,
) -> list[LLMPredicateComparisonResult]:
    """
    For the given product_id:
      - fetch all competitor details from Competitive Analysis
      - run the LLM comparison for each
      - save each result to Mongo (collection: predicate_llm_analysis)
    Returns all results in-memory as well.
    """

    # Always start clean
    await PredicateLLMAnalysis.find(
        PredicateLLMAnalysis.product_id == product_id
    ).delete_many()

    logger.info(f"Fetching competitive analysis for product_id={product_id}")
    ca_list = await get_competitive_analysis(product_id)
    if not ca_list:
        logger.warning("No Competitive Analysis records for product_id={}", product_id)
        return []
    
    # Resolve our product name once and persist it with each saved comparison
    product_name = await _resolve_product_name(product_id)

    picked = _pick_all_competitors(ca_list)
    logger.info(f"Picked {len(picked)} competitors for product_id={product_id}")
    results: List[LLMPredicateComparisonResult] = []

    for comp in picked:
        logger.info(
            f"Running LLM gap analysis for product_id={product_id}, competitor_id={getattr(comp, 'id', None)}"
        )
        res = await llm_gaps_and_suggestions_one(product_id, comp, model=model)
        results.append(res)

        # upsert save
        if overwrite:
            logger.info(
                f"Saving/updating PredicateLLMAnalysis for product_id={product_id}, competitor_id={res.competitor_id}"
            )
            existing = await PredicateLLMAnalysis.find_one({
                "product_id": product_id,
                "competitor_id": res.competitor_id,
            })
            if existing:
                existing.rows = res.rows
                existing.gaps = res.gaps
                existing.model_used = res.model_used
                existing.competitor_name = res.competitor_name
                # NEW: persist our product name
                try:
                    existing.product_name = product_name
                except Exception:
                    pass
                await existing.save()
                logger.debug(
                    f"Updated existing PredicateLLMAnalysis for product_id={product_id}, competitor_id={res.competitor_id}"
                )
            else:
                await PredicateLLMAnalysis(
                    product_id=product_id,
                    product_name=product_name,
                    competitor_id=res.competitor_id,
                    competitor_name=res.competitor_name,
                    rows=res.rows,
                    gaps=res.gaps,
                    model_used=res.model_used,
                ).insert()
                logger.debug(
                    f"Inserted new PredicateLLMAnalysis for product_id={product_id}, competitor_id={res.competitor_id}"
                )

    logger.info(
        f"Completed LLM gap analysis for all competitors for product_id={product_id}"
    )
    return results
