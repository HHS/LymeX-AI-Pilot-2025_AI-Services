import asyncio
from pathlib import Path
from fastapi import HTTPException
from loguru import logger

from src.modules.claim_builder.model import ClaimBuilder
from src.modules.claim_builder.utils import (
    _build_system_prompt,
    _download_to_tmp,
    _norm,
)
from src.services.openai.extract_files_data import extract_files_data
from src.modules.product_profile.model import ProductProfile
from src.modules.product_profile.storage import get_product_profile_documents
from src.modules.competitive_analysis.model import (
    CompetitiveAnalysis,
    CompetitiveAnalysisDetail,
)


async def do_analyze_claim_builder(product_id: str) -> None:
    # --------------------------------- gather data ---------------------------------- #
    # --- Prefer Competitive Analysis IFU; wait for it like we do for ProductProfile ---
    sleep_time = 5
    max_retries = 100  # 500 seconds max
    competitive_analysis = None
    for _ in range(max_retries):
        competitive_analysis = await CompetitiveAnalysis.find_one(
            CompetitiveAnalysis.product_id == product_id,
            CompetitiveAnalysis.is_self_analysis == True,
        )
        if competitive_analysis:
            break
        logger.warning("⏳  Waiting for Competitive-Analysis to be available...")
        await asyncio.sleep(sleep_time)
    else:
        raise HTTPException(404, "Competitive-Analysis not found for this product")

    competitive_analysis_detail = await CompetitiveAnalysisDetail.get(
        competitive_analysis.competitive_analysis_detail_id
    )
    ca_ifu_text = getattr(competitive_analysis_detail, "indications_for_use_statement", None)

    # Normalize IFU for prompt (CA preferred). If CA text is missing, fall back to ProductProfile.
    def _normalize_ifu(ifu_raw):
        if isinstance(ifu_raw, list):
            return "\n".join(str(x) for x in ifu_raw if x is not None)
        return str(ifu_raw) if ifu_raw is not None else ""

    ifu_text_for_prompt = _normalize_ifu(ca_ifu_text).strip()

    if not ifu_text_for_prompt:
        raise HTTPException(
            422,
            "Competitive Analysis IFU does not contains text - cannot analyse IFU",
        )

    logger.info("🧪 Using IFU from Competitive-Analysis for {} ({} chars): {!r}",
            product_id, len(ifu_text_for_prompt), ifu_text_for_prompt[:120])

    # Keep attaching Product Profile PDFs as supporting context (unchanged)
    docs = await get_product_profile_documents(product_id)


    # Prefer local cached path if storage layer provides it; otherwise download
    file_paths: list[Path] = []
    for d in docs:
        if getattr(d, "path", None):
            file_paths.append(Path(d.path))
        else:
            file_paths.append(await _download_to_tmp(d.url))

    # --- Load previously accepted items to suppress repeats on re-run ---
    previous_cb = await ClaimBuilder.find_one(ClaimBuilder.product_id == product_id)

    accepted_issue_titles: set[str] = set()
    accepted_missing_titles: set[str] = set()
    accepted_conflict_statements: set[str] = set()

    if previous_cb:
        # Issues (flag may not exist on older docs)
        for i in previous_cb.issues or []:
            if getattr(i, "accepted", None) is True and i.title:
                accepted_issue_titles.add(i.title.strip().lower())

        # Missing Elements
        for m in previous_cb.missing_elements or []:
            if getattr(m, "accepted", None) is True and m.title:
                accepted_missing_titles.add(m.title.strip().lower())

        # Phrase Conflicts – treat as accepted if an accepted_fix exists
        for p in previous_cb.phrase_conflicts or []:
            if getattr(p, "accepted_fix", None):
                if p.statement:
                    accepted_conflict_statements.add(p.statement.strip().lower())

    # --------------------------------- OpenAI call ---------------------------------- #
    system_prompt = _build_system_prompt(ClaimBuilder)
    """user_msg = (
        f"Below is the full IFU text for product **{product_id}**:\n\n{ifu_text}\n\n"
        "Please analyse the IFU and all attached PDFs."
    )
    """
    user_msg = (
        f"You are reviewing the following Indications-for-Use (IFU) for "
        f"product **{product_id}**:\n\n"
        "```text\n"
        f"{ifu_text_for_prompt}\n"
        "```\n\n"
        "• Identify every issue (missing element, clarity, refactoring). "
        "  **Severity must be exactly `LOW`, `MEDIUM`, or `CRITICAL`.** "  # to prevent wrong data
        "• Detect conflicts inside the IFU and against the PDFs if relevant. "
        "• Detect any phrase conflicts in refrence to regulatory standards."
        "Return a **single** JSON object that exactly matches the "
        "`ClaimBuilder` schema provided earlier.  No extra keys, "
        "no markdown, valid JSON only."
    )

    # --- Instruct model to NOT re-report accepted items ---
    if accepted_issue_titles or accepted_missing_titles or accepted_conflict_statements:
        user_msg += (
            "\n\nThe following items have ALREADY been accepted by the user in a"
            " prior run. DO NOT re-report them unless there is a NEW, materially"
            " different problem:\n"
        )
        if accepted_issue_titles:
            user_msg += "\n- Accepted Issues:\n" + "\n".join(
                f"  • {t}" for t in sorted(accepted_issue_titles)
            )
        if accepted_missing_titles:
            user_msg += "\n- Accepted Missing Elements:\n" + "\n".join(
                f"  • {t}" for t in sorted(accepted_missing_titles)
            )
        if accepted_conflict_statements:
            user_msg += "\n- Accepted Phrase Conflict statements:\n" + "\n".join(
                f"  • {t}" for t in sorted(accepted_conflict_statements)
            )

    result: ClaimBuilder = await extract_files_data(
        file_paths=file_paths,
        system_instruction=system_prompt,
        user_question=user_msg,
        model_class=ClaimBuilder,
    )

    # --- Suppress any items accepted in a prior run (backend guarantee) ---
    if getattr(result, "issues", None):
        result.issues = [
            i
            for i in result.issues
            if i.title and i.title.strip().lower() not in accepted_issue_titles
        ]

    if getattr(result, "missing_elements", None):
        result.missing_elements = [
            m
            for m in result.missing_elements
            if m.title and m.title.strip().lower() not in accepted_missing_titles
        ]

    if getattr(result, "phrase_conflicts", None):
        result.phrase_conflicts = [
            p
            for p in result.phrase_conflicts
            if p.statement
            and p.statement.strip().lower() not in accepted_conflict_statements
        ]

    # --------------------------------- DB insert ------------------------------------ #
    # clean old doc then insert the new one so _id stays stable
    # await ClaimBuilder.find(ClaimBuilder.product_id == product_id).delete_many()

    # --------------------------------- DB merge ------------------------------------ #
    # NOTE: at this point 'result' contains ONLY new/open items (accepted ones were filtered)

    # Load current doc (if any)
    existing_cb = await ClaimBuilder.find_one(ClaimBuilder.product_id == product_id)

    # We already fetched competitive_analysis_detail above; reuse it here to update draft content
    if 'competitive_analysis_detail' in locals() and competitive_analysis_detail:
        if existing_cb and (existing_cb.draft or result.draft):
            if existing_cb.draft:
                existing_cb.draft[0].content = competitive_analysis_detail.indications_for_use_statement
            elif result.draft:
                result.draft[0].content = competitive_analysis_detail.indications_for_use_statement
    else:
        logger.info("Competitive Analysis data not available for  {}", product_id)

    if existing_cb:
        # 1) Carry forward OPEN (not-accepted) items from the previous doc
        prev_open_issues = [
            i
            for i in (existing_cb.issues or [])
            if i.title and not getattr(i, "accepted", False)
        ]
        prev_open_missing = [
            m
            for m in (existing_cb.missing_elements or [])
            if m.title and not getattr(m, "accepted", False)
        ]
        prev_open_conflicts = [
            p
            for p in (existing_cb.phrase_conflicts or [])
            if p.statement and not getattr(p, "accepted_fix", False)
        ]

        prev_issue_keys = {_norm(i.title) for i in prev_open_issues}
        prev_missing_keys = {_norm(m.title) for m in prev_open_missing}
        prev_conflict_keys = {_norm(p.statement) for p in prev_open_conflicts}

        # 2) Add only genuinely new items (avoid dupes vs previous OPEN ones)
        new_issues = [
            i
            for i in (result.issues or [])
            if i.title and _norm(i.title) not in prev_issue_keys
        ]
        new_missing = [
            m
            for m in (result.missing_elements or [])
            if m.title and _norm(m.title) not in prev_missing_keys
        ]
        new_conflicts = [
            p
            for p in (result.phrase_conflicts or [])
            if p.statement and _norm(p.statement) not in prev_conflict_keys
        ]

        logger.debug(
            "Merge: prev_open issues/missing/conflicts = %d/%d/%d; new adds = %d/%d/%d",
            len(prev_open_issues),
            len(prev_open_missing),
            len(prev_open_conflicts),
            len(new_issues),
            len(new_missing),
            len(new_conflicts),
        )

        # 3) IMPORTANT: never replace with result.*; carry forward + append new
        existing_cb.issues = prev_open_issues + new_issues
        existing_cb.missing_elements = prev_open_missing + new_missing
        existing_cb.phrase_conflicts = prev_open_conflicts + new_conflicts

        existing_cb.is_user_input = False
        if existing_cb and existing_cb.missing_elements:
            for i, missing_element in enumerate(existing_cb.missing_elements):
                missing_element.id = i + 1
        if existing_cb and existing_cb.phrase_conflicts:
            for i, conflict in enumerate(existing_cb.phrase_conflicts):
                conflict.id = i
        await existing_cb.save()
    else:
        # First run: insert the fresh result as-is
        result.product_id = product_id
        result.is_user_input = False
        if existing_cb and existing_cb.missing_elements:
            for i, missing_element in enumerate(existing_cb.missing_elements):
                missing_element.id = i + 1
        if existing_cb and existing_cb.phrase_conflicts:
            for i, conflict in enumerate(existing_cb.phrase_conflicts):
                conflict.id = i
        for dr in result.draft:
            dr.submitted = False
            dr.accepted = False
            dr.reject_message = None
        await result.save()
