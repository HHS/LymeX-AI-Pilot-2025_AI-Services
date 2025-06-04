from pathlib import Path
from collections import defaultdict
import json
from typing import Dict, List
from .semantic_matcher import split_sentences, embed_sentences, best_match, _EMB

_TPL_DIR = Path(__file__).parent.parent / "resources" / "templates"

def _load_fields(pathway: str) -> List[str]:
    return json.loads((_TPL_DIR / f"{pathway}.json").read_text())

def detect_pathway(text: str) -> str:
    lo = text.lower()
    if "510(k)" in lo:
        return "510k"
    if "de novo" in lo:
        return "denovo"
    return "pma"

def check_template(pages) -> Dict:
    full = "\n".join(p.text for p in pages)
    pathway = detect_pathway(full)
    needed_fields = _load_fields(pathway)

    # sentence embedding once
    sents = split_sentences(full)
    vecs  = embed_sentences(sents)

    field_results = {}
    for field in needed_fields:
        found, _ = best_match(vecs, sents, field)
        field_results[field] = found

    return {
        "pathway": pathway,
        "fields": field_results,
        "complete": all(field_results.values()),
    }
