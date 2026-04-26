from __future__ import annotations
import uuid
import structlog
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    Fusion,
    FusionQuery,
    MatchValue,
    PointStruct,
    Prefetch,
    SparseIndexParams,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from app.core.config import get_settings
from app.rag.parser.chunker import TextChunk

log = structlog.get_logger()
settings = get_settings()

_client: QdrantClient | None = None

_DENSE_NAME = "dense"
_SPARSE_NAME = "sparse"


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
    return _client


def ensure_collection(collection_name: str) -> None:
    """
    Create collection with dense + sparse vector configs.
    If the collection exists but has the old single-vector schema (no sparse),
    it is recreated so hybrid search works correctly.
    """
    client = get_client()
    existing = {c.name for c in client.get_collections().collections}

    if collection_name in existing:
        info = client.get_collection(collection_name)
        # Named vector dict {"dense": ...} means new hybrid schema.
        # Old schema stores VectorParams directly (not a dict).
        vectors = info.config.params.vectors
        has_hybrid_schema = isinstance(vectors, dict) and _DENSE_NAME in vectors
        if has_hybrid_schema:
            return  # already on the correct schema
        log.warning(
            "qdrant.collection.schema_mismatch",
            name=collection_name,
            action="recreating with sparse vectors — re-ingest required",
        )
        client.delete_collection(collection_name)

    client.create_collection(
        collection_name=collection_name,
        vectors_config={
            _DENSE_NAME: VectorParams(
                size=settings.qdrant_vector_size,
                distance=Distance.COSINE,
            )
        },
        sparse_vectors_config={
            _SPARSE_NAME: SparseVectorParams(
                index=SparseIndexParams(on_disk=False)
            )
        },
    )
    log.info("qdrant.collection.created", name=collection_name)


def upsert_chunks(
    collection_name: str,
    chunks: list[TextChunk],
    dense_embeddings: list[list[float]],
    sparse_embeddings: list[SparseVector],
) -> None:
    client = get_client()
    ensure_collection(collection_name)

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector={_DENSE_NAME: dense_emb, _SPARSE_NAME: sparse_emb},
            payload={
                "text": chunk.text,
                "file_id": chunk.file_id,
                "page": chunk.page,
                "chunk_type": chunk.chunk_type.value,
                "chunk_index": chunk.chunk_index,
                "collection": chunk.metadata.get("collection", collection_name),
                **{k: v for k, v in chunk.metadata.items() if k != "collection"},
            },
        )
        for chunk, dense_emb, sparse_emb in zip(chunks, dense_embeddings, sparse_embeddings)
    ]

    client.upsert(collection_name=collection_name, points=points)
    log.info("qdrant.upsert", collection=collection_name, count=len(points))


def search(
    collection_name: str,
    query_vector: list[float],
    query_sparse: SparseVector,
    top_k: int = 5,
    file_id: str | None = None,
) -> list[dict]:
    """
    Hybrid search: dense cosine + BM25 sparse, fused with RRF.
    Each branch over-fetches 4× to give RRF enough candidates.
    """
    client = get_client()

    query_filter = None
    if file_id:
        query_filter = Filter(
            must=[FieldCondition(key="file_id", match=MatchValue(value=file_id))]
        )

    prefetch_limit = top_k * 4

    results = client.query_points(
        collection_name=collection_name,
        prefetch=[
            Prefetch(
                query=query_vector,
                using=_DENSE_NAME,
                limit=prefetch_limit,
                filter=query_filter,
            ),
            Prefetch(
                query=query_sparse,
                using=_SPARSE_NAME,
                limit=prefetch_limit,
                filter=query_filter,
            ),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        limit=top_k,
        with_payload=True,
    )

    return [
        {
            "text": hit.payload.get("text", ""),
            "file_id": hit.payload.get("file_id"),
            "page": hit.payload.get("page"),
            "chunk_type": hit.payload.get("chunk_type"),
            "score": hit.score,
        }
        for hit in results.points
    ]


def delete_by_file_id(collection_name: str, file_id: str) -> None:
    client = get_client()
    client.delete(
        collection_name=collection_name,
        points_selector=Filter(
            must=[FieldCondition(key="file_id", match=MatchValue(value=file_id))]
        ),
    )
    log.info("qdrant.delete", collection=collection_name, file_id=file_id)
