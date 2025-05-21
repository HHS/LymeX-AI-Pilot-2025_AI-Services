"""
app.extractor.text_extractor
----------------------------
Pure *text-only* extraction:
  • PDF (text layer), DOCX, plain-text files
  • Rejects scanned/image-only PDFs and all image formats
No OCR, no OpenAI import, no external APIs.
"""

from __future__ import annotations

import logging
import mimetypes
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import List

import pdfplumber                  # pdfplumber==0.11.*
try:
    import docx                    # python‑docx==1.1.*
except ImportError:                # pragma: no cover
    docx = None

log = logging.getLogger(__name__)


# --------------------------------------------------------------------------- exceptions
class UnsupportedFileError(ValueError):
    """Raised when a file violates text‑only constraints."""


# --------------------------------------------------------------------------- DTO
@dataclass
class Page:
    doc_id: str
    page_no: int
    text: str


# --------------------------------------------------------------------------- main extractor
class TextExtractor:
    """
    Usage
    -----
    pages = TextExtractor().extract("/tmp/sample.pdf")
    """

    SUPPORTED_MIME = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    }

    # .................................................................  public
    def extract(self, file_path: str | Path, *, doc_id: str | None = None) -> List[Page]:
        """Return list[Page] objects with raw text only."""
        file_path = Path(file_path)
        doc_id = doc_id or str(uuid.uuid4())

        mime, _ = mimetypes.guess_type(file_path)
        mime = (mime or "").lower()
        if mime not in self.SUPPORTED_MIME:
            raise UnsupportedFileError(f"Unsupported MIME type: {mime}")

        if mime == "application/pdf":
            return self._parse_pdf(file_path, doc_id)
        elif mime.endswith("document"):
            return self._parse_docx(file_path, doc_id)
        else:
            return self._parse_txt(file_path, doc_id)

    # ................................................................. parsers
    def _parse_pdf(self, path: Path, doc_id: str) -> List[Page]:
        pages: list[Page] = []
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text = (page.extract_text() or "").strip()
                if not text:
                    raise UnsupportedFileError(
                        f"{path.name} looks like a scanned/image-only PDF."
                    )
                pages.append(Page(doc_id, i, text))
        return pages

    def _parse_docx(self, path: Path, doc_id: str) -> List[Page]:
        if docx is None:
            raise RuntimeError("Install python-docx to handle DOCX files.")
        doc = docx.Document(path)
        text = "\n".join(p.text for p in doc.paragraphs)
        return [Page(doc_id, 1, text)]

    @staticmethod
    def _parse_txt(path: Path, doc_id: str) -> List[Page]:
        text = Path(path).read_text(encoding="utf-8", errors="ignore")
        return [Page(doc_id, 1, text)]
