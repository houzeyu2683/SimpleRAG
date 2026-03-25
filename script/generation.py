"""
generation.py — 用 Ollama 從 BBC 新聞文章自動生成 QA test set
用法: python script/generation.py
"""

import os
import json
import glob
import random
import requests

DATA_PATH = ".data/bbc"
OUTPUT_PATH = ".data/news/test.json"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"
NUM_ARTICLES = 25
RANDOM_SEED = 42

PROMPT_TEMPLATE = """以下是一篇新聞文章，請根據文章內容出一個問題，並提供正確答案。

要求：
- 問題必須可以從文章中找到答案
- 答案要具體、簡潔（1-3句話）
- 請用繁體中文
- 只輸出 JSON，格式如下：
{{"question": "問題", "ground_truth": "答案"}}

文章標題：{title}
文章內容：{content}

JSON 輸出："""


def getResponse(prompt: str) -> str:
    response = requests.post(OLLAMA_URL, json={
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }, timeout=60)
    return (response.json()["response"].strip())


def getDictionary(text: str) -> dict | None:
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        return (json.loads(text[start:end]))
    except Exception:
        return (None)


def runProgram() -> bool:
    files = glob.glob(f"{DATA_PATH}/*.json")
    random.seed(RANDOM_SEED)
    selected = random.sample(files, min(NUM_ARTICLES, len(files)))

    pairs = []
    for index, path in enumerate(selected, 1):
        with open(path, encoding="utf-8") as file:
            article = json.load(file)

        print(f"({index}/{len(selected)}) {article['title'][:30]}...")

        content = article.get("content", "")[:1000]
        prompt = PROMPT_TEMPLATE.format(title=article["title"], content=content)

        raw = getResponse(prompt)
        pair = getDictionary(raw)

        if pair and "question" in pair and "ground_truth" in pair:
            pairs.append(pair)
            print(f"  ✓ Q: {pair['question'][:40]}...")
        else:
            print(f"  ✗ 解析失敗，跳過")
        continue

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(pairs, file, ensure_ascii=False, indent=2)

    print(f"\n完成！共生成 {len(pairs)} 對 QA，存至 {OUTPUT_PATH}")

    return (True)


if __name__ == "__main__":
    runProgram()
