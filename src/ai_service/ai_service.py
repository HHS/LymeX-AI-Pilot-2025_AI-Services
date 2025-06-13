from __future__ import annotations

from typing import List, Dict
from pathlib import Path

from ai_service.extractor.text_extractor import TextExtractor, Page
from ai_service.analysis import qa_checker, template_checker, summarizer
#from tool_a.embeddings import get_embedder, vector_store    # optional

# ---- public DTO --------------------------------------------------------------
class DocResult(dict):
    """
    Dict-like container returned by `process_document()`.
    Keys:
        doc_id : str
        summary : str
        missing_questions : List[str]
        missing_template_fields : List[str]
    """

# ---- single entry‑point ------------------------------------------------------
def process_document(file_path: str | Path, *, embed: bool = False) -> DocResult:
    """
    Run the full pipeline on `file_path`, store vectors if `embed=True`,
    and return a DocResult with everything the back‑end needs.

    Raises
    ------
    UnsupportedFileError
        if file has no extractable text.
    """
    # 1.  Extract pages
    pages: List[Page] = TextExtractor().extract(file_path)
    full_text = "\n".join(p.text for p in pages)

    # 2.  Embeddings (optional)
    """if embed:
        emb = get_embedder()
        if emb:
            vectors = emb.embed([p.text for p in pages])
            vector_store.upsert(pages, vectors)"""   # implementation already in app.embeddings.vector_store

    # 3.  Analysis
    summary = summarizer.summarize(pages)      # ≤ 250 words
    qa_report = qa_checker.check_questions(pages)
    #tpl_report = template_checker.check_template(pages)

    # 4.  Assemble missing lists
    missing_q = [k for k, v in qa_report.items() if not v["found"]]
    #missing_tpl = [fld for fld, ok in tpl_report["fields"].items() if not ok]

    return DocResult(
        doc_id      = pages[0].doc_id,
        summary     = summary,
        missing_questions       = missing_q,
        #missing_template_fields = missing_tpl,
    )
