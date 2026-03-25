import datasets
import ragas
import ragas.metrics
import ragas.llms
import ragas.embeddings
import langchain_ollama
import langchain_huggingface

llm = ragas.llms.LangchainLLMWrapper(
    langchain_ollama.ChatOllama(model='qwen2.5:3b', temperature=0)
)
embedding = ragas.embeddings.LangchainEmbeddingsWrapper(
    langchain_huggingface.HuggingFaceEmbeddings(model_name='BAAI/bge-m3')
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
ragas.metrics.answer_relevancy.embeddings = embedding

data = {
    "question":     ["What is the rated power of HS-5102-12A1?"],
    "answer":       ["1KW"],
    "contexts":     [["## Electrical Specification\nRated power 1KW/1.2KW"]],
    "ground_truth": ["1KW"],
}
dataset = datasets.Dataset.from_dict(data)
result = ragas.evaluate(dataset=dataset, metrics=metrics, raise_exceptions=False)
print(result)
print(result.to_pandas().to_string())
