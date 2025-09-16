"""
OpenAI embedding backend.
Cost: $0.00002/1000 tokens on `text-embedding-3-small`.
"""
from typing import List, Sequence
import os, openai

_MODEL = "text-embedding-3-small"

class OpenAIEmbedder:
    def __init__(self, model: str = _MODEL, api_key: str | None = None):
        self.model = model
        self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        if not texts:
            return []
        res = self.client.embeddings.create(model=self.model, input=list(texts))
        return [d.embedding for d in res.data]
