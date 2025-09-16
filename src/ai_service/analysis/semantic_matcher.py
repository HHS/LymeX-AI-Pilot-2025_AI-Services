"""
Shared helper – embeds sentences once and offers fuzzy+semantic search.
"""
from pathlib import Path
from typing import List, Sequence, Tuple
import numpy as np
import spacy
from sentence_transformers import SentenceTransformer
from rapidfuzz.fuzz import partial_ratio
from rapidfuzz.utils import default_process
import subprocess, sys

try:
    _NLP = spacy.load("en_core_web_sm", disable=["ner", "parser"])
except OSError:
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
    _NLP = spacy.load("en_core_web_sm", disable=["ner", "parser"])

if not _NLP.has_pipe("sentencizer"):
    _NLP.add_pipe("sentencizer")

_EMB = SentenceTransformer("all-MiniLM-L6-v2")

def split_sentences(text: str) -> List[str]:
    doc = _NLP(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]

def embed_sentences(sents: Sequence[str]) -> np.ndarray:
    return _EMB.encode(sents, normalize_embeddings=True)

def best_match(
    sent_vectors: np.ndarray,
    sentences: Sequence[str],
    query: str,
    thresh_sem: float = 0.6,
    thresh_fuzzy: int = 80,
) -> Tuple[bool, List[int]]:
    """Return (found?, [sentence_indices])"""
    q_vec = _EMB.encode(query, normalize_embeddings=True)
    cos = np.dot(sent_vectors, q_vec)
    idx_sem = np.where(cos >= thresh_sem)[0].tolist()

    idx_fz = [
        i
        for i, s in enumerate(sentences)
        if partial_ratio(default_process(query), default_process(s)) >= thresh_fuzzy
    ]
    idx = sorted(set(idx_sem + idx_fz))
    return bool(idx), idx
