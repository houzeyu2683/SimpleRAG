"""
_ingest_.py — 載入資料、切塊、向量化，存入 ChromaDB
用法:
  python utility/_ingest_.py --config configuration/gaming.yaml   # Wikipedia 模式
  python utility/_ingest_.py --config configuration/news.yaml     # 本地 JSON 模式
"""

import os
import json
import glob
import time
import argparse
import yaml
import dotenv
import requests
import langchain_text_splitters
import langchain_huggingface
import langchain_chroma

dotenv.load_dotenv()

WIKI_API = "https://en.wikipedia.org/api/rest_v1/page/summary"
WIKI_SEARCH_API = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "SPfRAG/1.0 (RAG portfolio project; educational use)"}


def getConfiguration(path: str) -> dict:
    with open(path) as file:
        configuration = yaml.safe_load(file)
    return (configuration)


def getTitles(query: str, maximum: int) -> list:
    """用 Wikipedia 搜尋取得相關頁面標題。"""
    response = requests.get(WIKI_SEARCH_API, params={
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": maximum,
        "format": "json",
    }, headers=HEADERS, timeout=10)
    results = response.json().get("query", {}).get("search", [])
    return ([result["title"] for result in results])


def getPage(title: str) -> dict | None:
    """用 Wikipedia REST API 取得頁面全文。"""
    try:
        response = requests.get(
            f"{WIKI_API}/{title.replace(' ', '_')}",
            headers=HEADERS,
            timeout=10,
        )
        if response.status_code != 200:
            print(f"  [skip] {title} — HTTP {response.status_code}")
            return (None)

        detail = requests.get(WIKI_SEARCH_API, params={
            "action": "query",
            "prop": "extracts",
            "explaintext": True,
            "titles": title,
            "format": "json",
        }, headers=HEADERS, timeout=10)
        pages = detail.json().get("query", {}).get("pages", {})
        page = next(iter(pages.values()))

        if "missing" in page or not page.get("extract"):
            print(f"  [skip] {title} — 無內容")
            return (None)

        text = "\n".join(
            line for line in page["extract"].splitlines() if line.strip()
        )
        address = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        return ({"url": address, "title": title, "text": text})

    except Exception as error:
        print(f"  [skip] {title} — {error}")
        return (None)


def buildVectorstore(documents: list, configuration: dict) -> bool:
    """將文件切塊、embed，存入 ChromaDB。"""
    splitter = langchain_text_splitters.RecursiveCharacterTextSplitter(
        chunk_size=configuration["chunk_size"],
        chunk_overlap=configuration["chunk_overlap"],
    )

    texts, metadatas = [], []
    for document in documents:
        chunks = splitter.split_text(document["text"])
        for chunk in chunks:
            texts.append(chunk)
            metadatas.append({"title": document["title"], "url": document["url"]})
            continue
        continue

    print(f"共 {len(texts)} 個 chunks，開始 embedding...")

    embeddings = langchain_huggingface.HuggingFaceEmbeddings(
        model_name=configuration["embedding_model"]
    )

    langchain_chroma.Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        collection_name=configuration["collection_name"],
        persist_directory=f".chroma/{configuration['collection_name']}",
    )

    return (True)


def getDocuments(path: str) -> list:
    """從本地 JSON 檔案載入文件（每個 JSON 一篇文章）。"""
    documents = []
    for filepath in glob.glob(f"{path}/*.json"):
        with open(filepath, encoding="utf-8") as file:
            item = json.load(file)
        documents.append({
            "title": item.get("title", os.path.basename(filepath)),
            "url": item.get("link", filepath),
            "text": item.get("content", ""),
        })
        continue
    return (documents)


def runProgram(path: str) -> bool:
    configuration = getConfiguration(path)

    if "data_path" in configuration:
        print(f"[{configuration['domain']}] 從 {configuration['data_path']} 載入資料...")
        documents = getDocuments(configuration["data_path"])
        print(f"載入 {len(documents)} 篇文章")
    else:
        query = configuration.get("wiki_search_query", "Genshin Impact")
        print(f"[{configuration['domain']}] 從 Wikipedia 搜尋：{query}")
        titles = getTitles(query, configuration["max_pages"])
        print(f"找到 {len(titles)} 個頁面，開始抓取...")
        if not titles:
            print("錯誤：搜尋無結果。")
            return (True)
        documents = []
        for index, title in enumerate(titles, 1):
            print(f"  ({index}/{len(titles)}) {title}")
            document = getPage(title)
            if document:
                documents.append(document)
            time.sleep(0.3)
            continue
        print(f"\n成功抓取 {len(documents)} 個頁面")

    if not documents:
        print("錯誤：沒有資料。")
        return (True)

    buildVectorstore(documents, configuration)
    print(f"向量庫建立完成，collection: {configuration['collection_name']}")

    return (True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configuration/news.yaml")
    arguments = parser.parse_args()
    runProgram(arguments.config)
