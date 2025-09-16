from __future__ import annotations

import os, json
from typing import List, Dict, Iterable, AsyncIterator
from loguru import logger

S3_PREFIX = os.getenv("CT_SHARDS_S3_PREFIX", "clinical_trial_data/shards")

def _match_condition(rec: Dict, condition: str) -> bool:
    if not condition:
        return True
    conds: Iterable[str] = rec.get("conditions") or []
    q = condition.lower()
    return any(q in (c or "").lower() for c in conds)

def _match_sponsor(rec: Dict, sponsor: str) -> bool:
    if not sponsor:
        return True
    q = sponsor.lower()
    lead = (rec.get("sponsor") or "").lower()
    collabs = [str(x).lower() for x in (rec.get("collaborators") or [])]
    return (q in lead) or any(q in c for c in collabs)

def _to_v2_like(sys_rec: Dict) -> Dict:
    nct       = sys_rec.get("nct_id")
    title     = sys_rec.get("title")
    sponsor   = sys_rec.get("sponsor")
    collabs   = sys_rec.get("collaborators") or []
    status    = sys_rec.get("overall_status")
    phase     = sys_rec.get("phase")
    enroll    = sys_rec.get("enrollment")
    studytype = sys_rec.get("study_type")
    outcomes  = sys_rec.get("primary_outcomes") or []
    elig      = sys_rec.get("eligibility_text") or ""
    return {
        "protocolSection": {
            "identificationModule": {"nctId": nct, "briefTitle": title},
            "sponsorCollaboratorsModule": {
                "leadSponsor": {"name": sponsor} if sponsor else None,
                "collaborators": [{"name": c} for c in collabs] or None,
            },
            "statusModule": {"overallStatus": status},
            "designModule": {
                "phase": phase,
                "enrollmentInfo": {"count": enroll},
                "designInfo": {"designModel": studytype},
            },
            "outcomesModule": {"primaryOutcomes": [{"measure": m} for m in outcomes if m]},
            "eligibilityModule": {"eligibilityCriteria": elig},
        }
    }

async def _iter_s3_records(prefix: str) -> AsyncIterator[Dict]:
    from src.infrastructure.minio import list_objects, get_object
    objs = await list_objects(prefix)
    if not objs:
        logger.warning(f"[ct] No shard objects found under s3://<bucket>/{prefix}")
    for obj in objs:
        if getattr(obj, "is_dir", False):
            continue
        key = obj.object_name  # e.g. clinical_trial_data/shards/part-00000.jsonl
        try:
            raw = await get_object(key)  # bytes
        except Exception as e:
            logger.warning(f"[ct] failed to read {key}: {e}")
            continue
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception as e:
                logger.warning(f"[ct] bad JSON in {key}: {e}")

async def search_trials(condition: str, sponsor: str, page_size: int = 100) -> List[Dict]:
    """
    Read shards from S3/MinIO (S3_PREFIX) and filter by
    (condition AND sponsor/collaborator). Return v2-like dicts.
    """
    if not condition or not sponsor:
        return []

    results: List[Dict] = []
    async for rec in _iter_s3_records(S3_PREFIX):
        if _match_condition(rec, condition) and _match_sponsor(rec, sponsor):
            results.append(_to_v2_like(rec))
            if len(results) >= page_size:
                break
    return results
