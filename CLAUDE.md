# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SPfRAG** is a multi-domain RAG (Retrieval-Augmented Generation) system supporting natural language queries across three domains: finance, hardware, and gaming. The core RAG pipeline is shared; domain differences are isolated via YAML config files. Developed using **Vibe Coding** (AI-assisted development) — AI generates code, the developer owns architecture and evaluation decisions.

## Tech Stack

| Component | Choice |
|---|---|
| Framework | LangChain |
| Embedding | `text-embedding-3-small` (OpenAI) or `bge-m3` (local) |
| Vector DB | ChromaDB (local) or Qdrant (Docker) |
| LLM | GPT-4o-mini or Ollama (local) |
| Data ingestion | `pdfplumber` (PDF), `BeautifulSoup` (HTML) |
| Evaluation | RAGAS |
| UI | Gradio |

## Architecture

```
Data Sources (PDF / HTML / scraping)
    ↓
src/ingest.py     — load, clean, chunk, embed → Vector DB
src/retriever.py  — hybrid search (vector + BM25), optional re-ranking
src/chain.py      — LangChain RAG chain (retriever + LLM)
src/evaluate.py   — RAGAS evaluation against QA test sets
app.py            — Gradio UI
config/<domain>.yaml — per-domain settings (data path, chunking params, model choices)
```

Domain data lives under `data/finance/`, `data/hardware/`, `data/gaming/`. Switching domains means pointing config to a different data directory and Vector DB collection.

## Key Design Decisions (interview discussion points)

1. **Chunking strategy** — Fixed-size vs semantic chunking; evaluated with retrieval precision per domain. Finance/hardware PDFs need table-aware chunking; gaming wiki needs HTML cleanup first.
2. **Embedding model** — OpenAI vs local `bge-m3`; the tradeoff is cost/speed vs Chinese query quality.
3. **Hybrid retrieval** — Pure vector search vs BM25 hybrid; hybrid improves keyword queries (model numbers, company names, character names).
4. **Re-ranking** — Cohere Reranker or cross-encoder to limit context to top-3 chunks before sending to LLM.

## Evaluation

RAGAS metrics: `faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`. Each domain has a 20–30 QA pair test set. Run evaluation after each optimization step to record delta scores.

## Development Phases

1. **Phase 1** — Single domain (gaming) end-to-end: scrape Fandom Wiki → ChromaDB → basic QA
2. **Phase 2** — Add RAGAS evaluation, record baseline scores
3. **Phase 3** — Optimize: compare chunking strategies, add hybrid search, add re-ranking
4. **Phase 4** — Extend to finance and hardware domains
5. **Phase 5** — Gradio demo + document experiment results for interviews
