"""
_retriever_.py — 從 ChromaDB 做向量檢索
"""

import langchain_huggingface
import langchain_chroma


def getRetriever(configuration: dict) -> object:
    """載入已建好的 vectorstore，回傳 LangChain retriever。"""
    embeddings = langchain_huggingface.HuggingFaceEmbeddings(
        model_name=configuration["embedding_model"]
    )

    vectorstore = langchain_chroma.Chroma(
        collection_name=configuration["collection_name"],
        embedding_function=embeddings,
        persist_directory=f".chroma/{configuration['collection_name']}",
    )

    limit = configuration.get("retrieval_limit", 5)
    return (vectorstore.as_retriever(search_kwargs={"k": limit}))
