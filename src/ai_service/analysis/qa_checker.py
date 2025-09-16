# app/analysis/qa_checker.py  – v3 robust matcher
from pathlib import Path
from typing import Dict, List
import yaml
from ai_service.extractor.text_extractor import Page
from ai_service.analysis.semantic_matcher import split_sentences, embed_sentences, best_match, _EMB
from rapidfuzz.fuzz import partial_ratio
from rapidfuzz.utils import default_process

_Q_PATH = Path(__file__).parent.parent / "resources" / "device_description_questionnaire.yaml"
QUESTIONNAIRE = yaml.safe_load(_Q_PATH.read_text())

# ---------------- helpers ----------------------------------------------------
FUZZY_THRESH = 85          # a bit higher now that we check phrase-by-phrase
SEM_THRESH   = 0.58

def sentence_chunks(pages: List[Page]):
    sents, pages_of = [], []
    for pg in pages:
        # also split table-like lines on ':' to isolate headings
        for raw in split_sentences(pg.text):
            for part in raw.split(":"):
                txt = part.strip()
                if txt:
                    sents.append(txt)
                    pages_of.append(pg.page_no)
    return sents, pages_of

def phrase_found(phrase: str, sents: List[str], vecs):
    phrase_lc = phrase.lower()
    # 1) exact / substring
    for s in sents:
        if phrase_lc in s.lower():
            return True
    # 2) fuzzy
    for s in sents:
        if partial_ratio(default_process(phrase), default_process(s)) >= FUZZY_THRESH:
            return True
    # 3) semantic
    q_vec = _EMB.encode(phrase, normalize_embeddings=True)
    if (vecs @ q_vec).max() >= SEM_THRESH:
        return True
    return False
# -----------------------------------------------------------------------------

def check_questions(pages: List[Page]) -> Dict[str, dict]:
    sents, page_map = sentence_chunks(pages)
    vecs = embed_sentences(sents)

    report = {}
    for q in QUESTIONNAIRE:
        hit_pages = set()
        for phrase in q["key_phrases"]:
            # collect indices where phrase matches
            q_vec = _EMB.encode(phrase, normalize_embeddings=True)
            cos = (vecs @ q_vec)
            idx = [i for i, s in enumerate(sents) if
                   phrase.lower() in s.lower() or
                   partial_ratio(default_process(phrase), default_process(s)) >= FUZZY_THRESH or
                   cos[i] >= SEM_THRESH]
            hit_pages.update(page_map[i] for i in idx)
            if hit_pages:      # early stop if any match
                break
        report[q["id"]] = {
            "question": q["question"],
            "found": bool(hit_pages),
            "pages": sorted(hit_pages),
        }
    return report
