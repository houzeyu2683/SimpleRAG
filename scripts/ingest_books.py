"""
Batch ingest books/ dataset into Qdrant.

Usage:
    python scripts/ingest_books.py                  # all domains
    python scripts/ingest_books.py --domain ai      # single domain
    python scripts/ingest_books.py --resume         # skip already-indexed files
"""
import argparse
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from tqdm import tqdm

from app.core.config import get_settings
from app.rag.embedder.local_embedder import embed_texts
from app.rag.parser.chunker import chunk_parsed_document
from app.rag.parser.pdf_parser import parse_pdf
from app.rag.retriever.qdrant_retriever import (
    ensure_collection,
    get_client,
    upsert_chunks,
)

BOOKS_DIR = Path(__file__).parent.parent / "books"
DOMAINS = ["ai", "biology", "chemistry", "medicine", "physics"]
RESUME_FILE = Path(__file__).parent / ".ingest_progress.json"

settings = get_settings()


def load_progress() -> set[str]:
    if RESUME_FILE.exists():
        return set(json.loads(RESUME_FILE.read_text()))
    return set()


def save_progress(done: set[str]) -> None:
    RESUME_FILE.write_text(json.dumps(list(done)))


def ingest_domain(domain: str, resume: bool) -> dict:
    pdf_files = sorted((BOOKS_DIR / domain).glob("*.pdf"))
    if not pdf_files:
        print(f"[{domain}] No PDFs found, skipping.")
        return {"domain": domain, "total": 0, "indexed": 0, "errors": 0}

    collection_name = domain
    ensure_collection(collection_name)

    done = load_progress() if resume else set()
    stats = {"domain": domain, "total": len(pdf_files), "indexed": 0, "errors": 0, "skipped": 0}
    data_dir = Path(settings.data_dir) / "books"
    data_dir.mkdir(parents=True, exist_ok=True)

    for pdf_path in tqdm(pdf_files, desc=f"[{domain}]", unit="pdf"):
        key = f"{domain}/{pdf_path.name}"
        if resume and key in done:
            stats["skipped"] += 1
            continue

        file_id = str(uuid.uuid5(uuid.NAMESPACE_URL, key))
        try:
            parse_result = parse_pdf(pdf_path, file_id, data_dir)
            chunks = chunk_parsed_document(parse_result.chunks, file_id, collection_name)
            if not chunks:
                stats["errors"] += 1
                continue

            texts = [c.text for c in chunks]
            embeddings = embed_texts(texts, batch_size=32)
            upsert_chunks(collection_name, chunks, embeddings)

            done.add(key)
            save_progress(done)
            stats["indexed"] += 1
        except Exception as exc:
            print(f"\n  ERROR {pdf_path.name}: {exc}")
            stats["errors"] += 1

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest books dataset into Qdrant")
    parser.add_argument("--domain", choices=DOMAINS, help="Ingest a single domain")
    parser.add_argument("--resume", action="store_true", help="Skip already-indexed files")
    args = parser.parse_args()

    domains = [args.domain] if args.domain else DOMAINS
    all_stats = []

    for domain in domains:
        stats = ingest_domain(domain, resume=args.resume)
        all_stats.append(stats)

    print("\n── Ingest Summary ──────────────────────────")
    for s in all_stats:
        print(f"  {s['domain']:<12} total={s['total']}  indexed={s['indexed']}  skipped={s.get('skipped', 0)}  errors={s['errors']}")

    # Show Qdrant collection sizes
    client = get_client()
    print("\n── Qdrant Collections ──────────────────────")
    for col in client.get_collections().collections:
        if col.name in DOMAINS:
            info = client.get_collection(col.name)
            print(f"  {col.name:<12} vectors={info.vectors_count}")


if __name__ == "__main__":
    main()
