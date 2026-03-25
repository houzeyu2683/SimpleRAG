"""
_reranker_.py — 用 cross-encoder 對檢索結果重新排序
"""


def getReranker(retriever: object, configuration: dict) -> object:
    """在 base retriever 上包一層 cross-encoder reranker。"""
    import langchain_community.cross_encoders
    import langchain_classic.retrievers.document_compressors
    import langchain_classic.retrievers.contextual_compression

    model = langchain_community.cross_encoders.HuggingFaceCrossEncoder(
        model_name=configuration.get("rerank_model", "BAAI/bge-reranker-base"),
        model_kwargs={"device": "cpu"},
    )
    compressor = langchain_classic.retrievers.document_compressors.CrossEncoderReranker(
        model=model,
        top_n=configuration.get("rerank_limit", 3),
    )
    return (langchain_classic.retrievers.contextual_compression.ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=retriever,
    ))
