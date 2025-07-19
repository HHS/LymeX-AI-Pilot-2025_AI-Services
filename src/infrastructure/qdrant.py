from typing import List, Optional, TypedDict
from uuid import uuid4

from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
    PointStruct,
    ScoredPoint,
    VectorParams,
)

from src.environment import environment
from src.infrastructure.openai import get_openai_client
from src.modules.index_system_data.summarize_files import FileSummary

client = QdrantClient(
    url=environment.qdrant_url,
    port=environment.qdrant_port,
    prefer_grpc=False,
)

EMBEDDING_MODEL: str = "text-embedding-3-small"
EMBED_DIM: int = 1536

try:
    client.create_collection(
        collection_name="system_data",
        vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
    )
except Exception as e:
    if "already exists" in str(e).lower():
        # ignore, it’s fine
        pass
    else:
        raise


async def embed_text(text: str) -> List[float]:
    """
    Embed the given text into a high-dimensional vector.
    """
    openai_client = get_openai_client()
    resp = await openai_client.embeddings.create(input=[text], model=EMBEDDING_MODEL)
    # resp is a CreateEmbeddingResponse object, so access via attributes:
    return resp.data[0].embedding  # List[float]


async def add_document(filename: str, summary: FileSummary) -> None:
    """
    Add a new document point with filename and summary.
    """
    vector = await embed_text(summary.summary)
    payload = {
        "filename": filename,
        "summary": summary.summary,
        "product_name": summary.files[0].product_name if summary.files else "Unknown",
    }
    logger.info(f"Adding document {filename} with payload: {payload}")
    point = PointStruct(
        id=uuid4().int >> 64,
        vector=vector,
        payload=payload,
    )
    client.upsert(
        collection_name="system_data",
        points=[point],
    )


def delete_document(filename: str) -> None:
    """
    Delete a document point by filename.
    """
    filt = Filter(
        must=[FieldCondition(key="filename", match=MatchValue(value=filename))]
    )
    client.delete(
        collection_name="system_data",
        points_selector=FilterSelector(filter=filt),
        wait=True,  # optional: wait until Qdrant has acknowledged deletion
    )


class DocumentFilename(TypedDict):
    id: str
    filename: Optional[str]


def get_all_documents() -> List[DocumentFilename]:
    """
    Returns a list of dicts with 'id' and 'filename' for all documents.
    """
    result = client.scroll(
        collection_name="system_data",
        with_payload=True,
        with_vectors=False,
    )
    documents: List[DocumentFilename] = [
        {
            "id": str(point.id),
            "filename": point.payload.get("filename") if point.payload else None,
        }
        for point in result[0]
    ]
    return documents


def get_by_filename(filename: str) -> List[PointStruct]:
    """
    Returns all PointStructs whose payload.filename exactly matches.
    """
    filt = Filter(
        must=[FieldCondition(key="filename", match=MatchValue(value=filename))]
    )
    result = client.scroll(
        collection_name="system_data",
        filter=filt,
        with_payload=True,
        with_vector=True,
    )
    return result  # List[PointStruct]


async def search_similar(summary: str, top_k: int = 5) -> List[ScoredPoint]:
    """
    Embeds the query summary and returns the top_k most similar points.
    """
    q_vector = await embed_text(summary)
    hits = client.search(
        collection_name="system_data",
        query_vector=q_vector,
        limit=top_k,
        with_payload=True,
        with_vectors=False,  # <-- renamed here
    )
    return hits  # List[ScoredPoint]
