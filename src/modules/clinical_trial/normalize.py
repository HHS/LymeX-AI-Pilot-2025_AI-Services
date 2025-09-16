from typing import Dict, Any, List, Optional
from .schema import ClinicalTrialStatus

def _safe_int(x) -> Optional[int]:
    try:
        return int(x) if x is not None else None
    except Exception:
        return None

def _map_status(s: Optional[str]) -> ClinicalTrialStatus:
    s = (s or "").lower()
    if "not yet recruit" in s or "pending" in s or "plan" in s:
        return ClinicalTrialStatus.PLANNED
    if "recruit" in s:
        return ClinicalTrialStatus.RECRUITING
    if "complete" in s or "terminated" in s or "suspended" in s:
        return ClinicalTrialStatus.COMPLETED
    return ClinicalTrialStatus.ACTIVE

def to_internal(study: Dict[str, Any], product_id: str) -> Dict[str, Any]:
    ps = study.get("protocolSection", {}) or {}
    ident = ps.get("identificationModule", {}) or {}
    sponsor_mod = ps.get("sponsorCollaboratorsModule", {}) or {}
    design_mod = ps.get("designModule", {}) or {}
    outcomes_mod = ps.get("outcomesModule", {}) or {}
    elig_mod = ps.get("eligibilityModule", {}) or {}
    status_mod = ps.get("statusModule", {}) or {}

    nct_id = ident.get("nctId")
    title = ident.get("officialTitle") or ident.get("briefTitle") or (nct_id or "Unknown Title")

    # Study design: try common fields
    design_info = design_mod.get("designInfo", {}) or {}
    design = (
        design_info.get("designAllocation")
        or design_info.get("designModel")
        or design_info.get("designPrimaryPurpose")
        or design_info.get("designObservationalModel")
    )
    if isinstance(design, list):
        design = ", ".join([str(x) for x in design])

    enrollment = _safe_int((design_mod.get("enrollmentInfo", {}) or {}).get("count"))

    # Primary outcomes (names only for the card)
    primary_outcomes: List[str] = []
    for o in outcomes_mod.get("primaryOutcomes") or []:
        m = o.get("measure")
        if m:
            primary_outcomes.append(m)

    # Single-line outcome for backward-compat
    outcome = primary_outcomes[0] if primary_outcomes else "See primary outcomes"

    # Inclusion criteria: split text blob into bullets
    raw = (elig_mod.get("eligibilityCriteria") or "").strip()
    inclusion = [line.strip("-• ").strip() for line in raw.splitlines() if line.strip()][:30]

    overall_status = status_mod.get("overallStatus")
    status = _map_status(overall_status)

    sponsor_name = None
    lead = sponsor_mod.get("leadSponsor") or {}
    if isinstance(lead, dict):
        sponsor_name = lead.get("name")

    protocol_url = f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else None

    # Phase can be text like "Phase 3" or a list in v2
    phase_val = design_mod.get("phases") or design_mod.get("phase")
    if isinstance(phase_val, list):
        phase_val = ", ".join(phase_val)

    return {
        "product_id": str(product_id),
        "nct_id": nct_id,
        "name": title,
        "sponsor": sponsor_name or "",
        "study_design": design or "",
        "enrollment": enrollment or 0,
        "status": status,
        "phase": phase_val or None,
        "outcome": outcome,
        "primary_outcomes": primary_outcomes,
        "inclusion_criteria": inclusion,
        "protocol_url": protocol_url,
        "summary_url": protocol_url,
        "marked": False,
    }
