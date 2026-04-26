"""
RAG quality evaluation — retrieves sample queries per domain and prints results for manual inspection.

Usage:
    python scripts/eval_rag.py
    python scripts/eval_rag.py --domain ai --top-k 5
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.rag.embedder.local_embedder import embed_query
from app.rag.retriever.qdrant_retriever import get_client, search

SAMPLE_QUERIES: dict[str, list[str]] = {
    "ai": [
        "What are the main challenges in training large language models?",
        "How does attention mechanism work in transformers?",
        "What is reinforcement learning from human feedback?",
    ],
    "biology": [
        "What is the role of mitochondria in cellular respiration?",
        "How does DNA replication ensure fidelity?",
        "What are the mechanisms of natural selection?",
    ],
    "chemistry": [
        "What is the mechanism of enzyme catalysis?",
        "How do polar solvents affect reaction rates?",
        "What are the properties of transition metals?",
    ],
    "medicine": [
        "What are the risk factors for cardiovascular disease?",
        "How do beta-blockers affect heart rate?",
        "What is the mechanism of action of antibiotics?",
    ],
    "physics": [
        "What is quantum entanglement?",
        "How does the Higgs boson give particles mass?",
        "What are the implications of the uncertainty principle?",
    ],
}


def eval_domain(domain: str, top_k: int) -> None:
    client = get_client()
    existing = {c.name for c in client.get_collections().collections}
    if domain not in existing:
        print(f"[{domain}] Collection not found — run ingest_books.py first.\n")
        return

    queries = SAMPLE_QUERIES.get(domain, [])
    print(f"\n{'='*60}")
    print(f"Domain: {domain}")
    print(f"{'='*60}")

    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        vector = embed_query(query)
        hits = search(domain, vector, top_k=top_k)
        for i, hit in enumerate(hits, 1):
            print(f"  [{i}] page={hit['page']}  score={hit['score']:.3f}  type={hit['chunk_type']}")
            print(f"      {hit['text'][:200].replace(chr(10), ' ')}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate RAG retrieval quality")
    parser.add_argument("--domain", choices=list(SAMPLE_QUERIES.keys()), help="Evaluate single domain")
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()

    domains = [args.domain] if args.domain else list(SAMPLE_QUERIES.keys())
    for domain in domains:
        eval_domain(domain, args.top_k)


if __name__ == "__main__":
    main()
