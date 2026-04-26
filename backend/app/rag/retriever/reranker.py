from __future__ import annotations
import structlog

log = structlog.get_logger()

_reranker = None
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def get_reranker():
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder  # lazy import
        log.info("reranker.loading", model=RERANKER_MODEL)
        _reranker = CrossEncoder(RERANKER_MODEL)
        log.info("reranker.ready")
    return _reranker


def rerank(query: str, hits: list[dict], top_n: int) -> list[dict]:
    if not hits:
        return []

    reranker = get_reranker()
    pairs = [(query, hit["text"]) for hit in hits]
    scores = reranker.predict(pairs)

    ranked = sorted(
        zip(hits, scores),
        key=lambda x: x[1],
        reverse=True,
    )
    return [hit for hit, _ in ranked[:top_n]]
