#!/usr/bin/env python3
"""
CSV → JSONL shards stored in a local folder for upload to S3 by your senior.

Input CSV columns you showed:
- NCT Number, Study Title, Study URL, Study Status, Brief Summary, Study Results,
  Conditions, Interventions, Primary Outcome Measures, Sponsor, Collaborators,
  Phases, Enrollment, Study Type, Study Design

Output folder layout (hand this folder to your senior):
  system_data/clinical_trials/shards/
    part-00000.jsonl
    part-00001.jsonl
    ...

Each line in .jsonl is one trial with a consistent schema used by the app.
"""

import json, sys
from pathlib import Path
import pandas as pd

OUT_DIR = Path("C:/Users/yishu/Downloads/shards")  # <— zip and give this folder
CSV_PATH = Path("C:/Users/yishu/Downloads/ctg-studies - Copy.csv")                 # put CSV file here
CHUNK = 50_000
SHARD_SIZE = 50_000

def _split_list(val: str | None) -> list[str]:
    if not val or pd.isna(val): return []
    s = str(val).replace("\r\n","\n").replace("\r","\n").replace("|",";").replace("\n",";")
    parts = []
    for seg in s.split(";"):
        seg = seg.strip()
        if not seg: continue
        for piece in seg.split(","):
            piece = piece.strip()
            if piece: parts.append(piece)
    # de-dupe, keep order
    seen, out = set(), []
    for x in parts:
        k = x.lower()
        if k not in seen:
            seen.add(k); out.append(x)
    return out

def _norm_str(x):
    if x is None or (isinstance(x, float) and pd.isna(x)): return None
    s = str(x).strip()
    return s or None

def _norm_int(x):
    if x is None or (isinstance(x, float) and pd.isna(x)): return None
    try: return int(float(str(x).replace(",", "").strip()))
    except Exception: return None

def _row_to_rec(row: pd.Series) -> dict | None:
    nct = _norm_str(row.get("NCT Number"))
    if not nct: return None
    rec = {
        "nct_id": nct,
        "title": _norm_str(row.get("Study Title")),
        "sponsor": _norm_str(row.get("Sponsor")),
        "collaborators": _split_list(row.get("Collaborators")),
        "conditions": _split_list(row.get("Conditions")),
        "phase": _norm_str(row.get("Phases")),  # e.g. "Phase 2"
        "enrollment": _norm_int(row.get("Enrollment")),
        "overall_status": _norm_str(row.get("Study Status")),
        "primary_outcomes": _split_list(row.get("Primary Outcome Measures")),
        "eligibility_text": None,  # CSV doesn’t have it; can be enriched later
        "study_type": _norm_str(row.get("Study Type")),
        "study_design": _norm_str(row.get("Study Design")),
        "protocol_url": f"https://clinicaltrials.gov/study/{nct}",
    }
    return rec

def main():
    if not CSV_PATH.exists():
        raise SystemExit(f"CSV not found: {CSV_PATH}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shard_idx = 0
    written_in_shard = 0
    shard = (OUT_DIR / f"part-{shard_idx:05d}.jsonl").open("w", encoding="utf-8")
    total = 0

    usecols = [
        "NCT Number","Study Title","Study URL","Study Status","Brief Summary",
        "Study Results","Conditions","Interventions","Primary Outcome Measures",
        "Sponsor","Collaborators","Phases","Enrollment","Study Type","Study Design"
    ]

    for chunk in pd.read_csv(CSV_PATH, usecols=usecols, chunksize=CHUNK, dtype=str, keep_default_na=True):
        for _, row in chunk.iterrows():
            rec = _row_to_rec(row)
            if not rec: continue
            shard.write(json.dumps(rec, ensure_ascii=False) + "\n")
            total += 1
            written_in_shard += 1
            if written_in_shard >= SHARD_SIZE:
                shard.close()
                shard_idx += 1
                written_in_shard = 0
                shard = (OUT_DIR / f"part-{shard_idx:05d}.jsonl").open("w", encoding="utf-8")

    shard.close()
    if (OUT_DIR / f"part-{shard_idx:05d}.jsonl").stat().st_size == 0:
        (OUT_DIR / f"part-{shard_idx:05d}.jsonl").unlink(missing_ok=True)

    print(f"Done. Wrote ~{total} records across {shard_idx + 1} shard(s) into {OUT_DIR}")

if __name__ == "__main__":
    main()
