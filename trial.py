#python - <<'PY'
from pathlib import Path
import os, sys
# ----- make repo root importable (exactly what test_pipeline does)
ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT))
# ----- now import and run
from app.extractor.text_extractor import TextExtractor
from app.embeddings import get_embedder

pages = TextExtractor().extract("sample.pdf")      # adjust path
print("Extracted", len(pages), "pages")

print("EMBED_MODE =", os.getenv("EMBED_MODE"))
embedder = get_embedder()
print("Embedder object: ", embedder)                        # EMBED_MODE env var decides

if embedder:
    vecs = embedder.embed([p.text for p in pages])
    print("Generated", len(vecs), "vectors")

for p in pages:
    preview = (p.text.strip()[:200] + "…") if len(p.text) > 200 else p.text
    print(f"\n--- Page {p.page_no} preview ---\n{preview}")
#PY
