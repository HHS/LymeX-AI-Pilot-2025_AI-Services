"""
Pure text‑only extractor (PDF, DOCX, TXT)
• Tighter pdfplumber layout params  → fewer joined words
• Text normaliser (_clean)          → remove soft‑hyphens, weird spaces, ligatures
• Header/footer de‑duplication      → higher Word Accuracy
• Skips empty pages instead of raising unsupported error
"""

from __future__ import annotations
import logging, mimetypes, uuid, re, unicodedata as ud
from dataclasses import dataclass
from pathlib import Path
from typing import List

import pdfplumber
try:
    import docx
except ImportError:
    docx = None

log = logging.getLogger(__name__)

class UnsupportedFileError(ValueError): ...

@dataclass
class Page:
    doc_id: str
    page_no: int
    text: str

# --------------------------------------------------------------------- helpers

def _clean(txt: str) -> str:
    """Unicode‑normalise, drop soft‑hyphens, collapse whitespace."""
    txt = ud.normalize("NFKC", txt)
    txt = txt.replace("\u00ad", "")                       # soft hyphen
    txt = re.sub(r"-\s*\n\s*", "", txt)                  # hyphen‑linebreak
    txt = re.sub(r"\s+", " ", txt)                       # collapse spaces
    return txt.strip()

HEADER_RE = re.compile(r"K\d{6,7}.*Page \d+ of \d+", re.I)

def _strip_header(line: str) -> str:
    return "" if HEADER_RE.search(line) else line

# --------------------------------------------------------------------- extractor

class TextExtractor:
    SUPPORTED_MIME = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    }

    # ................................................................. public API
    def extract(self, path: str | Path, *, doc_id: str | None = None) -> List[Page]:
        path = Path(path)
        doc_id = doc_id or str(uuid.uuid4())

        mime, _ = mimetypes.guess_type(path)
        mime = (mime or "").lower()
        if mime == "application/pdf":
            return self._parse_pdf(path, doc_id)
        if mime.endswith("document"):
            return self._parse_docx(path, doc_id)
        if mime.startswith("text/"):
            return self._parse_txt(path, doc_id)
        raise UnsupportedFileError(f"Unsupported MIME: {mime}")

    # ................................................................. PDF
    def _parse_pdf(self, path: Path, doc_id: str) -> List[Page]:
        pages: list[Page] = []
        lap = dict(char_margin=1.0, word_margin=0.08, line_margin=0.1)
        with pdfplumber.open(path, laparams=lap) as pdf:
            for i, pg in enumerate(pdf.pages, start=1):
                raw = pg.extract_text(x_tolerance=2, y_tolerance=2) or ""
                # strip recurring header/footer lines
                lines = [_strip_header(l) for l in raw.splitlines()]
                txt = _clean("\n".join(l for l in lines if l))
                if not txt:
                    log.warning("%s p.%s has no extractable text", path.name, i)
                    continue
                pages.append(Page(doc_id, i, txt))
        if not pages:
            raise UnsupportedFileError(f"{path.name} appears to be scanned only.")
        return pages

    # ................................................................. DOCX / TXT
    def _parse_docx(self, path: Path, doc_id: str) -> List[Page]:
        if docx is None:
            raise RuntimeError("python-docx not installed.")
        doc = docx.Document(path)
        text = _clean("\n".join(p.text for p in doc.paragraphs))
        return [Page(doc_id, 1, text)]

    def _parse_txt(self, path: Path, doc_id: str) -> List[Page]:
        text = _clean(Path(path).read_text(encoding="utf‑8", errors="ignore"))
        return [Page(doc_id, 1, text)]
