from __future__ import annotations
from fastapi import APIRouter, HTTPException, status
from app.api.deps import CurrentUser
from app.rag.embedder.local_embedder import embed_query
from app.rag.retriever.qdrant_retriever import search
from app.schemas.document import SearchRequest, SearchResult

router = APIRouter()


@router.post("", response_model=list[SearchResult])
async def semantic_search(req: SearchRequest, _: CurrentUser):
    if req.top_k < 1 or req.top_k > 20:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="top_k must be between 1 and 20")

    query_vector = embed_query(req.query)
    hits = search(
        collection_name=req.collection_name,
        query_vector=query_vector,
        top_k=req.top_k,
        file_id=req.file_id,
    )

    return [
        SearchResult(
            text=h["text"],
            file_id=h["file_id"],
            page=h["page"],
            chunk_type=h["chunk_type"],
            score=h["score"],
            preview_url=f"/api/v1/documents/{h['file_id']}/page?page={h['page']}",
        )
        for h in hits
    ]
