# tests/test_pipeline.py
"""
Integration test for app.extractor + app.embeddings.

Usage:
    pytest -q  (recommended)
    or simply: python tests/test_pipeline.py <path-to-pdf>
"""
import os
import sys
from pathlib import Path

import pytest

# --------------- Adjust this path if your repo layout is different ----------
ROOT = Path(__file__).resolve().parents[1]          # repo root
sys.path.append(str(ROOT))                          # so `app.` is importable

from app.extractor.text_extractor import TextExtractor, UnsupportedFileError     # noqa: E402
from app.embeddings import get_embedder                                               # noqa: E402

# --------------------------------------------------------------------------- helpers
PDF_SAMPLE = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "sample.pdf")

@pytest.mark.skipif(not PDF_SAMPLE.exists(), reason="sample PDF not found")
def test_extraction_then_embedding():
    """End‑to‑end: extract text → optional embeddings."""

    # ----------- 1. Extract
    extractor = TextExtractor()
    pages = extractor.extract(PDF_SAMPLE)

    # Basic sanity checks
    assert len(pages) > 0, "No pages returned"
    assert all(p.text.strip() for p in pages), "Blank page text detected"
    print(f"[OK] Extracted {len(pages)} pages from {PDF_SAMPLE.name}")

    # ----------- 2. Embed  (only if EMBED_MODE != 'none')
    embedder = get_embedder()          # resolves via env var EMBED_MODE
    if embedder is None:
        pytest.skip("Embedding disabled (EMBED_MODE=none)")
    vectors = embedder.embed([p.text for p in pages])

    # Expect one vector per page, dimensions > 0
    assert len(vectors) == len(pages)
    assert len(vectors[0]) > 0
    print(f"[OK] Generated {len(vectors)} embeddings via {embedder.__class__.__name__}")

# --------------------------------------------------------------------------- CLI fallback
if __name__ == "__main__":
    # Allow `python tests/test_pipeline.py mydoc.pdf` without pytest
    try:
        test_extraction_then_embedding()  # type: ignore[misc]
        print("✅  All checks passed.")
    except UnsupportedFileError as e:
        print(f"❌  UnsupportedFileError: {e}")
        sys.exit(1)
    except AssertionError as e:
        print(f"❌  Assertion failed: {e}")
        sys.exit(1)
