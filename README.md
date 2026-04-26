# RAGSystem

A production-grade Retrieval-Augmented Generation (RAG) system for scientific PDF documents. Supports multi-user authentication, hybrid search, cross-encoder reranking, streaming responses, and per-page image previews — all running locally on a single GPU machine.

---

## Architecture Overview

```
Frontend (React + Vite)
    │  REST / SSE  JWT Bearer
    ▼
Backend (FastAPI)  ──── MariaDB (users / documents / collections)
    │                ── Qdrant  (dense + sparse vectors)
    │                ── Redis   (Celery broker + ingest pub/sub)
    ▼
Celery Worker  ──────── Local Disk (PDFs / page images)
    │
    ├── PDF Parser (PyMuPDF + pdfplumber)
    ├── Dense Embedder  (bge-m3, 1024-dim)
    └── Sparse Embedder (Qdrant BM25)

Query Pipeline (FastAPI async)
    ├── Hybrid Retrieve  (dense Prefetch + sparse Prefetch → RRF)
    ├── Cross-Encoder Rerank  (ms-marco-MiniLM-L-6-v2)
    └── Stream LLM  (Ollama llama3:latest, SSE)
```

Full Mermaid diagrams: [`arch/service-architecture.md`](arch/service-architecture.md) · [`arch/embedding-flow.md`](arch/embedding-flow.md)

---

## Key Technical Decisions

### Hybrid Search (Dense + Sparse → RRF)
Dense-only embeddings miss exact-keyword matches (model names, paper IDs, acronyms). Sparse BM25 alone misses semantic similarity. We run both in parallel inside Qdrant using named vectors and fuse with Reciprocal Rank Fusion (RRF), which is parameter-free and robust.

```
Prefetch dense  (cosine, top-20) ─┐
                                   ├─ FusionQuery(RRF) → top-5
Prefetch sparse (BM25,  top-20) ─┘
```

### Cross-Encoder Reranker
Bi-encoder retrieval ranks by vector similarity, not actual relevance. The cross-encoder (`ms-marco-MiniLM-L-6-v2`) scores each (query, passage) pair jointly — slower but more accurate. Applied after retrieval to re-score top-5 and return top-3.

### Streaming Architecture
The ingestion pipeline publishes status events to Redis pub/sub. The FastAPI SSE endpoint subscribes and forwards them to the browser in real time (parsing → chunking → embedding → indexing → done). Query responses stream token-by-token from Ollama over the same SSE connection.

### Page Image Previews
Every citation includes a `preview_url` pointing to `GET /api/v1/documents/{file_id}/page?page=N`. The endpoint renders the PDF page on-the-fly using PyMuPDF at 2× zoom and returns a PNG. Authentication uses a query-parameter token (`?token=`) so `<img>` tags can load the image without a custom fetch.

---

## Evolution from SimpleRAG

This project is the production evolution of **[SimpleRAG](https://github.com/houzeyu2683/SimpleRAG)**, a config-driven RAG system for querying industrial product datasheets built with LangChain + ChromaDB + Gradio.

| Dimension | SimpleRAG | RAGSystem |
|-----------|-----------|-----------|
| **Retrieval** | Dense-only (ChromaDB cosine) | Hybrid: dense + BM25 sparse → RRF fusion |
| **Reranking** | None | Cross-encoder (ms-marco-MiniLM-L-6-v2) |
| **PDF Parsing** | MarkdownHeaderTextSplitter + RecursiveCharacterTextSplitter | PyMuPDF heading detection + pdfplumber table extraction |
| **Framework** | LangChain abstraction | Custom FastAPI pipeline (no framework lock-in) |
| **UI** | Gradio | React 18 + TypeScript + Tailwind |
| **Auth** | None | JWT multi-user + RBAC |
| **Ingestion** | Synchronous | Async Celery worker with real-time SSE progress |
| **LLM** | Ollama qwen2.5:3b | Ollama llama3:latest (streaming) |
| **Embedder** | BAAI/bge-m3 | BAAI/bge-m3 (same, proven in SimpleRAG) |
| **Evaluation** | RAGAS framework | — |

SimpleRAG validated the core retrieval approach and identified dense-only search as a bottleneck when documents share similar boilerplate content. RAGSystem addresses this by adding sparse BM25 — which excels at exact-keyword matching — fused via RRF, eliminating the need for the metadata-filtering workaround that SimpleRAG required for multi-model datasheets.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS v4, Zustand, TanStack Query |
| Backend | Python 3.10, FastAPI, SQLAlchemy 2.0 async, Alembic |
| Task Queue | Celery 5, Redis |
| Vector DB | Qdrant (hybrid: named dense + sparse vectors) |
| Relational DB | MariaDB |
| Dense Embedder | `BAAI/bge-m3` via sentence-transformers (CPU, 1024-dim) |
| Sparse Embedder | `Qdrant/bm25` via fastembed |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| LLM | Ollama `llama3:latest` (local GPU, streamed) |
| PDF Parsing | PyMuPDF (text + images), pdfplumber (tables) |

---

## Features

- **Multi-user system** — JWT access + refresh tokens, role-based access control (admin / user)
- **Collection management** — group documents into named collections, each with its own Qdrant collection
- **Async ingestion** — PDF → parse → chunk → embed → index, with real-time progress via SSE
- **Hybrid retrieval** — dense cosine + BM25 sparse with RRF fusion, no tuning required
- **Reranking** — cross-encoder rescores retrieved passages before generation
- **Streaming chat** — token-by-token SSE with chat history (last 6 turns)
- **Citations** — each answer includes source passages with page numbers, relevance scores, and page image previews
- **Dark UI** — glassmorphism design with animated background

---

## Project Structure

```
backend/
  app/
    api/v1/         # FastAPI routers (auth, chat, documents, collections)
    core/           # config, security, RBAC
    models/         # SQLAlchemy ORM models
    rag/
      parser/       # pdf_parser.py (PyMuPDF + pdfplumber), chunker.py
      embedder/     # local_embedder.py (bge-m3), sparse_embedder.py (BM25)
      retriever/    # qdrant_retriever.py (hybrid search), reranker.py
      generator/    # ollama_client.py (streaming), prompt_builder.py
    tasks/          # Celery ingest_task.py
  alembic/          # DB migrations

frontend/
  src/
    components/     # chat/, layout/ — React components
    pages/          # auth/, chat/ — page views
    store/          # Zustand stores (auth, chat)
    hooks/          # useChat, useAuth, useWebSocket

arch/               # Mermaid architecture diagrams
```

---

## Local Development

**Prerequisites:** Python 3.10+, Node 20+, Docker (MariaDB + Qdrant + Redis), Ollama

```bash
# Start infrastructure
docker compose up -d mariadb qdrant redis

# Backend
cd backend
pip install -e ".[dev]"
cp .env.example .env          # fill in values
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Celery worker (separate terminal)
celery -A app.tasks.celery_app worker --loglevel=info -Q ingest --concurrency=1 -n ingest@linux

# Frontend
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`, register an account, create a collection, upload a PDF, and start chatting.

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | MariaDB connection string (`mysql+aiomysql://...`) |
| `QDRANT_HOST` / `QDRANT_PORT` | Qdrant server address |
| `REDIS_URL` | Redis connection URL |
| `OLLAMA_BASE_URL` | Ollama server (e.g. `http://localhost:11434`) |
| `OLLAMA_LLM_MODEL` | Model name (e.g. `llama3:latest`) |
| `EMBED_MODEL` | HuggingFace model ID for dense embeddings |
| `UPLOAD_DIR` | Where uploaded PDFs are stored |
| `DATA_DIR` | Root for parsed data and page images |
| `JWT_SECRET_KEY` | Secret for signing JWT tokens |
