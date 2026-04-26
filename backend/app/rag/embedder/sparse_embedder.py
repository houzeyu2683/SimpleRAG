from __future__ import annotations
import structlog
from qdrant_client.models import SparseVector

log = structlog.get_logger()

_model = None


def get_model():
    global _model
    if _model is None:
        from fastembed import SparseTextEmbedding  # lazy import
        log.info("sparse_embedder.loading", model="Qdrant/bm25")
        _model = SparseTextEmbedding(model_name="Qdrant/bm25")
        log.info("sparse_embedder.ready")
    return _model


def embed_sparse(texts: list[str]) -> list[SparseVector]:
    """BM25 document embeddings — used at ingestion time."""
    model = get_model()
    return [
        SparseVector(indices=r.indices.tolist(), values=r.values.tolist())
        for r in model.embed(texts)
    ]


def embed_sparse_query(text: str) -> SparseVector:
    """BM25 query embedding — IDF weighting differs from document embedding."""
    model = get_model()
    result = next(model.query_embed(text))
    return SparseVector(indices=result.indices.tolist(), values=result.values.tolist())
