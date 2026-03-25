# SPfRAG 開發紀錄 — Summary 1

## 完成進度

- **Phase 1** ✅ — 單一領域（Gaming）end-to-end 跑通
- **Phase 2** ✅ — RAGAS 評估，取得 baseline 分數
- **Phase 3** 🔲 — 優化中

---

## 技術選型決策

| 元件 | 最終選擇 | 淘汰的選項 | 原因 |
|---|---|---|---|
| 資料來源 | Wikipedia API | Fandom Wiki、genshin.dev、gamekee | Fandom 被 Cloudflare 擋；genshin.dev API 下線；gamekee JS 渲染 |
| Embedding | `all-MiniLM-L6-v2`（本地） | Google `text-embedding-004`、`gemini-embedding-001` | Google free tier 每分鐘 100 次不夠用 |
| LLM（RAG chain） | Groq `llama-3.1-8b-instant` | Google `gemini-1.5-flash`、`gemini-2.0-flash` | Gemini 模型下線或 free tier limit 為 0 |
| LLM（RAGAS 評估） | Ollama `llama3:8b`（本地 GPU） | Groq | Groq 不支援 `n > 1`，RAGAS 評估需要多次生成 |
| Vector DB | ChromaDB（本地） | Supabase | Portfolio 不需要登入系統，ChromaDB 零設定 |

---

## Baseline 評估結果（Phase 2）

資料：Wikipedia，50 頁，chunk_size=500，5 個 QA pairs

| 指標 | 分數 |
|---|---|
| faithfulness | 0.600 |
| answer_relevancy | 0.499 |
| context_precision | 0.631 |
| context_recall | 0.900 |

---

## 發現的問題

**1. 資料缺漏（最嚴重）**
- Wikipedia 沒有 Fischl 等角色的獨立頁面
- 用 `"Genshin Impact character"` 關鍵字搜到的頁面品質不一，缺乏角色細節
- 導致 answer_relevancy 低、部分問題直接答不出來

**2. Chunk 雜訊**
- "List of Genshin Impact characters" 頁面被切成很多 chunk，一直搶佔 retrieval 名額
- chunk_size=500 偏小，每塊內容不夠豐富
- 導致 context_precision 只有 0.631

**3. Groq 不適合 RAGAS 評估**
- RAGAS 需要 `n > 1` 的多次生成，Groq 不支援
- 改用 Ollama 本地跑，RTX 3060 12GB 夠用

---

## Phase 3 優化計畫

**方向一：改善資料品質**
- 改 `ingest.py`：針對角色名字直接搜 Wikipedia（`"Hu Tao Genshin Impact"`）
- 過濾 "List of" 類型頁面

**方向二：改善 Chunking**
- chunk_size: 500 → 1000

**方向三：加入 Hybrid Search**
- 現在：純向量搜尋
- 目標：向量 + BM25，用 LangChain `EnsembleRetriever` 組合
- 預期改善：對角色名、技能名等關鍵字查詢效果更好

執行順序：先改資料 → 重跑評估記錄分數變化 → 再加 hybrid search → 再評估

---

## 面試話術方向

> 「我用 RAGAS 量化評估，發現 context_recall 已經 0.9 但 precision 只有 0.63，代表找得到但找回來的有雜訊。我追蹤到根本原因是 List 類型頁面佔據 retrieval 名額，以及資料來源對特定角色覆蓋不足，所以 Phase 3 針對這兩個問題優化。」
