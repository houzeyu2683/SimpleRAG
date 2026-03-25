"""
evaluation.py — 用 RAGAS 評估 RAG pipeline 品質
用法: python evaluation.py --config configuration/news.yaml
"""

import json
import argparse
import yaml
import math
import warnings
import dotenv
import datasets
import ragas
import ragas.metrics
import ragas.llms
import ragas.embeddings
import langchain_ollama
import langchain_huggingface
import utility

warnings.filterwarnings("ignore")
dotenv.load_dotenv()

def getConfiguration(path: str) -> dict:
    with open(path) as file:
        configuration = yaml.safe_load(file)
    return (configuration)


def getDataset(pairs: list, retriever: object, chain: object) -> object:
    questions, answers, contexts, ground_truths = [], [], [], []

    for index, pair in enumerate(pairs, 1):
        question = pair["question"]
        print(f"  ({index}/{len(pairs)}) {question}")

        documents = retriever.invoke(question)
        answer = chain.invoke(question)

        questions.append(question)
        answers.append(answer)
        contexts.append([document.page_content for document in documents])
        ground_truths.append(pair["ground_truth"])
        continue

    return (datasets.Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    }))


def runProgram(path: str, prompt: str | None = None, experiment: str | None = None) -> bool:
    configuration = getConfiguration(path)
    if prompt:
        configuration["prompt_version"] = prompt
    test_path = configuration.get("qa_test_path", f".data/{configuration['domain']}/test.json")

    with open(test_path) as file:
        pairs = json.load(file)

    print(f"載入 {len(pairs)} 個 QA pairs")

    retriever = utility.getRetriever(configuration)
    if configuration.get("reranking", False):
        retriever = utility.getReranker(retriever, configuration)
    chain = utility.getChain(retriever, configuration)

    print("生成 RAG 回答中...")
    data = getDataset(pairs, retriever, chain)

    llm = ragas.llms.LangchainLLMWrapper(langchain_ollama.ChatOllama(
        model=configuration.get("llm_model", "qwen2.5:3b"),
        temperature=0,
        timeout=300,
    ))
    embeddings = ragas.embeddings.LangchainEmbeddingsWrapper(
        langchain_huggingface.HuggingFaceEmbeddings(model_name=configuration["embedding_model"])
    )

    metrics = [
        ragas.metrics.faithfulness,
        ragas.metrics.answer_relevancy,
        ragas.metrics.context_precision,
        ragas.metrics.context_recall,
    ]
    for metric in metrics:
        metric.llm = llm
        continue
    ragas.metrics.answer_relevancy.embeddings = embeddings

    print("\n開始 RAGAS 評估...")
    result = ragas.evaluate(dataset=data, metrics=metrics, raise_exceptions=False)

    print("\n===== 評估結果 =====")
    frame = result.to_pandas()
    skip = {"question", "answer", "contexts", "ground_truth", "user_input", "response", "retrieved_contexts", "reference"}
    columns = [column for column in frame.columns if column not in skip]
    print(frame.to_string())

    print("\n平均分數：")
    for column in columns:
        value = frame[column].mean()
        print(f"  {column}: {value:.3f}" if not math.isnan(value) else f"  {column}: N/A")
        continue

    label = experiment if experiment else configuration.get("prompt_version", "baseline")
    output = f".data/{configuration['domain']}/result_{label}.csv"
    frame.to_csv(output, index=False)
    print(f"\n結果已存至 {output}")

    return (True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configuration/news.yaml")
    parser.add_argument("--prompt", default=None)
    parser.add_argument("--experiment", default=None)
    arguments = parser.parse_args()
    runProgram(arguments.config, arguments.prompt, arguments.experiment)
