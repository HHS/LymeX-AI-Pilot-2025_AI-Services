"""
CPU-only, licence-free embedding backend using Sentence-Transformers.
Model: all-MiniLM-L6-v2 (384-dim, ~90 MB).
"""
from typing import List, Sequence
from sentence_transformers import SentenceTransformer   # sentence-transformers>=2.7

class LocalEmbedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()
