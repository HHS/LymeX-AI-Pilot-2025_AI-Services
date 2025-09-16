"""
app.embeddings
==============
Quick helper to pick an embedding backend from settings:

    from tool_a.embeddings import get_embedder
    embedder = get_embedder()        # returns OpenAIEmbedder | LocalEmbedder | None
"""
from typing import Protocol, Sequence, List, Optional
from importlib import import_module
import os

class EmbedderProtocol(Protocol):
    def embed(self, texts: Sequence[str]) -> List[List[float]]: ...

_BACKENDS = {
    "openai": "app.embeddings.embedder_openai:OpenAIEmbedder",
    "local":  "app.embeddings.embedder_local:LocalEmbedder",
    "none":   None,
}

def get_embedder(kind: str | None = None) -> Optional[EmbedderProtocol]:
    kind = (kind or os.getenv("EMBED_MODE", "none")).lower()
    target = _BACKENDS.get(kind)
    if target is None:
        return None
    module_path, cls_name = target.split(":")
    module = import_module(module_path)
    return getattr(module, cls_name)()          # type: ignore[return-value]
