"""
evaluate_10_pdfs.py  – v2
──────────────────────────────────────────────────────────────────
• Reads ground‑truth CSV (semicolon‑separated)
• Evaluates *every* PDF in PDF_DIR (expects their stems to match
  submission_number entries in the CSV)
• Metrics per page:
      Word Accuracy   (100 % – jiwer WER)
      Order Score     (ROUGE‑L F1)
      Meaning Score   (MiniLM cosine)
• Prints a per‑PDF summary table and an overall average line
──────────────────────────────────────────────────────────────────
pip install jiwer rouge-score sentence-transformers numpy pandas
python -m nltk.downloader punkt   # one‑time for ROUGE tokenizer
"""
from pathlib import Path
import re, unicodedata as ud
import numpy as np
import pandas as pd
from jiwer import wer
from rouge_score import rouge_scorer
from sentence_transformers import SentenceTransformer

# ── CONFIG ───────────────────────────────────────────────────────
CSV_PATH = Path("ivd_decision_summary_text.csv")  # ground truth
PDF_DIR  = Path("pdfs")                           # folder with 10 PDFs
# ─────────────────────────────────────────────────────────────────

# ----- extractor -------------------------------------------------
from app.extractor.text_extractor import TextExtractor
textract = TextExtractor()

# ----- helpers ---------------------------------------------------
def clean(txt: str) -> str:
    txt = ud.normalize("NFKC", txt)
    txt = txt.replace("\u00ad", "")                         # soft hyphen
    txt = re.sub(r"-\s*\n\s*", "", txt)                    # hyphen + NL
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt

scorer   = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
embedder = SentenceTransformer("all-MiniLM-L6-v2")
def cosine(a, b) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))

def metric_scores(gt: str, pred: str):
    gt, pred = clean(gt), clean(pred)
    word_acc = max(0.0, 1.0 - wer(gt, pred))
    rouge    = scorer.score(gt, pred)["rougeL"].fmeasure
    vec_gt   = embedder.encode(gt, normalize_embeddings=True)
    vec_pr   = embedder.encode(pred, normalize_embeddings=True)
    meaning  = cosine(vec_gt, vec_pr)
    return word_acc, rouge, meaning

# ----- load ground truth ----------------------------------------
gt = pd.read_csv(CSV_PATH, sep=';', dtype={'submission_number': str, 'page_number': int})
gt.set_index(['submission_number', 'page_number'], inplace=True)

subs_in_dir = {p.stem for p in PDF_DIR.glob("*.pdf")}
gt = gt[gt.index.get_level_values(0).isin(subs_in_dir)]

# ----- iterate PDFs ---------------------------------------------
rows = []

for pdf_path in PDF_DIR.glob("*.pdf"):
    sub = pdf_path.stem
    pages = textract.extract(str(pdf_path))
    for pg in pages:
        key = (sub, pg.page_no)
        if key not in gt.index:
            continue  # skip cover/blank pages without GT
        word_acc, rouge, meaning = metric_scores(gt.loc[key, 'text_embedded'], pg.text)
        rows.append(dict(submission_number=sub, page_number=pg.page_no,
                         word_acc=word_acc, order=rouge, meaning=meaning))

df = pd.DataFrame(rows)

# ----- aggregate results ----------------------------------------
per_pdf = df.groupby('submission_number').agg(
    word_acc_mean=('word_acc', 'mean'),
    order_mean   =('order',    'mean'),
    meaning_mean =('meaning',  'mean')
).sort_index()

overall = per_pdf.mean()

# ----- print -----------------------------------------------------
print("\n── PER‑PDF QUALITY METRICS ───────────────────────────────")
print(per_pdf.to_markdown(floatfmt=".3f"))

print("\n=== AVERAGE ACROSS THE 10 PDFs ===")
print(f"Word Accuracy …………… {overall['word_acc_mean']*100:5.1f}%")
print(f"Order Score (ROUGE‑L) … {overall['order_mean']*100:5.1f}%")
print(f"Meaning Score ………… {overall['meaning_mean']*100:5.1f}%")
