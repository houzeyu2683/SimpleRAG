from __future__ import annotations
import structlog
from app.core.config import get_settings

log = structlog.get_logger()
settings = get_settings()

_model = None


def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer  # lazy — avoids torchcodec at import time
        log.info("embedder.loading", model=settings.embed_model)
        _model = SentenceTransformer(settings.embed_model, device="cpu")
        log.info("embedder.ready")
    return _model


def embed_texts(texts: list[str], batch_size: int = 64) -> list[list[float]]:
    model = get_model()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=False,
        normalize_embeddings=True,
    )
    return embeddings.tolist()


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
