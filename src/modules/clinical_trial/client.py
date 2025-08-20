from __future__ import annotations

import os, json
from pathlib import Path
from typing import List, Dict, Iterable
from loguru import logger

# ENV:
# - CT_SHARDS_LOCAL_DIR  -> e.g. "system_data/clinical_trials/shards" (for local tests)
# - CT_SHARDS_S3_PREFIX  -> override S3 prefix if data uploaded somewhere else
LOCAL_DIR = os.getenv("CT_SHARDS_LOCAL_DIR")
S3_PREFIX = os.getenv("CT_SHARDS_S3_PREFIX", "system_data/clinical_trials/shards")

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
    nct = sys_rec.get("nct_id")
    title = sys_rec.get("title")
    sponsor = sys_rec.get("sponsor")
    collabs = sys_rec.get("collaborators") or []
    status = sys_rec.get("overall_status")
    phase = sys_rec.get("phase")
    enroll = sys_rec.get("enrollment")
    study_type = sys_rec.get("study_type")
    outcomes = sys_rec.get("primary_outcomes") or []
    elig_text = sys_rec.get("eligibility_text") or ""

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
                "designInfo": {"designModel": study_type},
            },
            "outcomesModule": {"primaryOutcomes": [{"measure": m} for m in outcomes if m]},
            "eligibilityModule": {"eligibilityCriteria": elig_text},
        }
    }

def _iter_local_records(dir_path: str):
    d = Path(dir_path)
    if not d.exists():
        logger.warning(f"[ct] Local shards dir not found: {d}")
        return
    for fp in sorted(d.glob("*.jsonl")):
        try:
            with fp.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line: 
                        continue
                    try:
                        yield json.loads(line)
                    except Exception as e:
                        logger.warning(f"[ct] bad JSON in {fp.name}: {e}")
        except Exception as e:
            logger.warning(f"[ct] failed to read {fp}: {e}")

async def _iter_s3_records(prefix: str):
    from src.infrastructure.minio import list_objects, get_object
    objs = await list_objects(prefix)
    for obj in objs:
        if getattr(obj, "is_dir", False):
            continue
        key = obj.object_name
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
    Filter trials from shards by (condition AND sponsor/collaborator),
    return v2-like dicts (max page_size).
    """
    if not condition or not sponsor:
        return []

    results: List[Dict] = []

    # Prefer local during tests
    if LOCAL_DIR:
        for rec in _iter_local_records(LOCAL_DIR):
            if _match_condition(rec, condition) and _match_sponsor(rec, sponsor):
                results.append(_to_v2_like(rec))
                if len(results) >= page_size:
                    return results
        return results

    # Otherwise read from S3/MinIO
    async for rec in _iter_s3_records(S3_PREFIX):
        if _match_condition(rec, condition) and _match_sponsor(rec, sponsor):
            results.append(_to_v2_like(rec))
            if len(results) >= page_size:
                return results

    return results
