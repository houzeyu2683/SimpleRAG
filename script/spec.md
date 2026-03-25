# RAG Project Spec — Multi-Domain Knowledge Assistant

## 專案目標

建立一個可跨領域部署的 RAG（Retrieval-Augmented Generation）系統，透過切換資料來源，支援金融、硬體、遊戲三個領域的自然語言查詢。核心架構共用，領域差異以設定檔隔離。

開發方式：Vibe Coding（AI-assisted development）

---

## 系統架構

```
資料來源（PDF / HTML / 爬蟲）
    ↓
資料清洗 & 切塊（Chunking）
    ↓
Embedding（文字向量化）
    ↓
Vector DB（向量儲存）
    ↓
Query → Retrieval → LLM → 回答
```

---

## Tech Stack

| 元件 | 選擇 | 理由 |
|---|---|---|
| Framework | LangChain | 生態成熟，元件可替換 |
| Embedding Model | `text-embedding-3-small`（OpenAI）或 `bge-m3`（本地） | 前者快速驗證，後者免費可離線 |
| Vector DB | ChromaDB（本地）或 Qdrant（Docker） | 輕量，不需要雲端服務 |
| LLM | GPT-4o-mini（API）或 Ollama 本地模型 | 依預算選擇 |
| 資料爬取 | BeautifulSoup / pdfplumber | PDF 和 HTML 各自處理 |
| 評估 | RAGAS | 標準 RAG 評估框架 |
| UI | Gradio | 快速建立 demo 介面 |

---

## 領域設定

### 金融（Finance）
- **資料來源：** 台灣上市公司年報 PDF（公開資訊觀測站）、金管會法規文件
- **爬取方式：** 直接下載 PDF（`pdfplumber` 解析）
- **使用情境：** 「XX 公司 2023 年的營收是多少？」「這條法規對銀行的要求是什麼？」
- **特殊處理：** 財報有大量表格，chunking 時需保留表格上下文

### 硬體（Hardware）
- **資料來源：** 晶片 / 元件 Datasheet PDF（TI、NVIDIA、聯發科官網）
- **爬取方式：** 直接下載 PDF
- **使用情境：** 「這顆晶片的工作電壓範圍？」「支援哪些通訊協定？」
- **特殊處理：** 技術文件有大量數字與單位，chunking 不能斷在規格中間

### 遊戲（Gaming）
- **資料來源：** Fandom Wiki（選一款大型遊戲，例如原神、Elden Ring）
- **爬取方式：** BeautifulSoup 爬取 Wiki 頁面
- **使用情境：** 「這個角色的技能效果是什麼？」「這個 Boss 的弱點？」
- **特殊處理：** Wiki 頁面結構較雜，需清理 HTML tag 和導覽列內容

---

## 核心決策點（面試時的話題）

這些是刻意設計的技術決策，每一個都能在面試中展開討論：

### 1. Chunking 策略
- **問題：** Fixed-size chunking 會切斷語意，Semantic chunking 成本高
- **實作：** 比較兩種策略，用 retrieval precision 評估差異
- **結論：** 記錄哪個領域適合哪種策略，以及原因

### 2. Embedding Model 選擇
- **問題：** OpenAI embedding 快但有費用；本地 `bge-m3` 支援中文但需要 GPU
- **實作：** 兩者都跑，比較中文查詢的 retrieval 品質
- **結論：** 記錄在中文財報上的差異

### 3. Retrieval 策略
- **問題：** 純向量搜尋對關鍵字查詢效果差（例如型號、公司名）
- **實作：** 加入 BM25 hybrid search，比較純向量 vs hybrid 的 F1
- **結論：** 記錄哪個領域 hybrid 改善最明顯

### 4. Context Window 管理
- **問題：** Retrieve 回來的 chunk 太多會超過 context window
- **實作：** 加入 re-ranking（Cohere Reranker 或 cross-encoder），只送 top-3
- **結論：** 比較有無 re-ranking 的答案品質

---

## 評估指標（用 RAGAS）

| 指標 | 說明 |
|---|---|
| `faithfulness` | 回答是否忠實於檢索到的文件 |
| `answer_relevancy` | 回答是否切題 |
| `context_precision` | 檢索到的 chunk 是否精準 |
| `context_recall` | 相關資訊是否都被找到 |

每個領域準備 20–30 個 QA pair 作為 test set，跑完後記錄分數。

---

## 專案結構

```
SPfRAG/
├── spec.md                  # 本文件
├── config/
│   ├── finance.yaml         # 金融領域設定
│   ├── hardware.yaml        # 硬體領域設定
│   └── gaming.yaml          # 遊戲領域設定
├── data/
│   ├── finance/             # 原始 PDF
│   ├── hardware/            # 原始 PDF
│   └── gaming/              # 爬取的 HTML/文字
├── src/
│   ├── ingest.py            # 資料載入 & 切塊 & 向量化
│   ├── retriever.py         # Retrieval 邏輯（含 hybrid search）
│   ├── chain.py             # LangChain RAG chain
│   └── evaluate.py          # RAGAS 評估
├── app.py                   # Gradio UI
└── notebooks/
    └── experiments.ipynb    # chunking / embedding 比較實驗
```

---

## 開發順序

1. **Phase 1 — 跑通單一領域（遊戲，最簡單）**
   - 爬取 Fandom Wiki → ChromaDB → 基本問答跑通

2. **Phase 2 — 加入評估**
   - 準備 QA test set → 跑 RAGAS → 記錄 baseline 分數

3. **Phase 3 — 優化決策點**
   - 比較 chunking 策略
   - 加入 hybrid search
   - 加入 re-ranking

4. **Phase 4 — 擴展其他領域**
   - 複製設定，換資料來源，重新跑評估

5. **Phase 5 — UI + 整理**
   - Gradio demo
   - 整理實驗結果，準備面試話題

---

## 面試時怎麼說

> 「我用 vibe coding 的方式開發這個專案——由 AI 生成程式碼框架，我負責架構設計、技術決策與評估。這讓我能在短時間內完成跨三個領域的 RAG 系統，並專注在真正有價值的部分：chunking 策略比較、hybrid search 實作、以及用 RAGAS 量化評估各領域的檢索品質。」
