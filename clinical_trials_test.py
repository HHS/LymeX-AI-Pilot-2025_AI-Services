#!/usr/bin/env python3
"""
Clinical Trials E2E test using LOCAL shards (no S3/HTTP, no Redis).
- Sets CT_SHARDS_LOCAL_DIR *before* importing analyze/service/client
- Inits Beanie + Mongo
- Runs analyze_clinical_trial() and prints saved rows
"""

import os, sys, asyncio, argparse
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from loguru import logger
from unittest.mock import patch

os.environ.update(
    MONGO_URI="mongodb://localhost:27017",
    MONGO_DB="dummy",
    REDIS_HOST="localhost",
    REDIS_PORT="6379",
    REDIS_DB="0",
    MINIO_INTERNAL_ENDPOINT="https://s3.us-west-2.amazonaws.com",
    MINIO_ROOT_USER=os.getenv("MINIO_ROOT_USER", "test-user"),
    MINIO_ROOT_PASSWORD=os.getenv("MINIO_ROOT_PASSWORD", "test-password"),
    MINIO_BUCKET="nois2-192-dev",
    OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", "test-key"),
    CT_SHARDS_S3_PREFIX="clinical_trial_data/shards"
)

# ---------- defaults ----------
DEFAULT_PRODUCT_ID = "TEST-PP-001"
DEFAULT_CONDITION  = "Lyme Borreliosis"
DEFAULT_SPONSORS   = "Sorlandet Hospital HF"
DEFAULT_MONGO_URI  = "mongodb://localhost:27017"
DEFAULT_MONGO_DB   = "dummy"
#DEFAULT_SHARDS_DIR = r"C:\Users\yishu\Downloads\shards"   # your local shards folder

# keep stdlib-only imports above; import project modules *after* env is set


def _fmt_list(items, max_items=5):
    items = items or []
    if len(items) <= max_items:
        return "; ".join(items) if items else "-"
    return "; ".join(items[:max_items]) + f" … (+{len(items)-max_items} more)"


class DummyLock:
    async def acquire(self, blocking=False): return True
    async def release(self): return True


async def main():
    ap = argparse.ArgumentParser("Clinical Trials (local shards) test")
    ap.add_argument("--product-id", default=DEFAULT_PRODUCT_ID)
    ap.add_argument("--condition",  default=DEFAULT_CONDITION)
    ap.add_argument("--sponsors",   default=DEFAULT_SPONSORS)
    args = ap.parse_args([] if len(sys.argv) == 1 else None)

    # ---- now import project modules (client sees env) ----
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from src.modules.clinical_trial.model import ClinicalTrial
    from src.modules.clinical_trial.analyze import analyze_clinical_trial

    # confirm S3 objects are visible under the prefix
    try:
        from src.infrastructure.minio import list_objects
        objs = await list_objects(os.environ["CT_SHARDS_S3_PREFIX"])
        sample = [o.object_name for o in objs[:5]]
        logger.info(f"S3 prefix OK. Sample objects: {sample}")
    except Exception as e:
        logger.error(f"Could not list S3 prefix {os.environ['CT_SHARDS_S3_PREFIX']}: {e}")
        return 2

    # ---- init db ----
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DB")]
    await init_beanie(database=db, document_models=[ClinicalTrial])

    sponsors = [s.strip() for s in (args.sponsors or "").split(",") if s.strip()]
    if not sponsors:
        logger.error("❌ No sponsors parsed from --sponsors"); return 2

    # clean previous
    await ClinicalTrial.find(ClinicalTrial.product_id == args.product_id).delete_many()

    # mock Redis lock only (no need to patch MinIO since we read local files)
    with patch("src.modules.clinical_trial.analyze.redis_client.lock", return_value=DummyLock()):
        rows = await analyze_clinical_trial(args.product_id, args.condition, sponsors)  # returns saved docs
        logger.info(f"Analyzer saved rows: {len(rows)}")

    # print results
    rows = await ClinicalTrial.find(ClinicalTrial.product_id == args.product_id).to_list()
    print(f"\n=== Retrieved {len(rows)} trials for product_id={args.product_id} ===\n")
    for i, t in enumerate(rows, 1):
        status = getattr(t, "status", "-")
        try: status = getattr(status, "value", status)
        except Exception: pass
        print(f"[{i}] {t.name} (NCT: {getattr(t, 'nct_id', '-')})")
        print(f"    Sponsor         : {t.sponsor or '-'}")
        print(f"    Study Design    : {t.study_design or '-'}")
        print(f"    Enrollment      : {t.enrollment or '-'}")
        print(f"    Status / Phase  : {status}/{getattr(t, 'phase', '-')}")
        print(f"    Primary Outcomes: {_fmt_list(getattr(t, 'primary_outcomes', []))}")
        print(f"    Protocol URL    : {getattr(t, 'protocol_url', '-')}")
        print()

    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
