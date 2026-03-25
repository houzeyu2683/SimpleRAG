import yaml
import openai
import ragas.llms
import ragas.embeddings
import ragas.metrics.collections
with open('.secret.yaml', encoding='utf-8') as paper:
    secret = yaml.safe_load(paper)
    pass

client = openai.AsyncOpenAI(
    api_key=secret['GROQ_API_KEY'],
    base_url="https://api.groq.com/openai/v1",
)
llm = ragas.llms.llm_factory(model="llama-3.1-8b-instant", client=client)
embedding = ragas.embeddings.HuggingFaceEmbeddings(model='BAAI/bge-m3')

faithfulness = ragas.metrics.collections.Faithfulness(llm=llm)
relevancy = ragas.metrics.collections.AnswerRelevancy(llm=llm, embeddings=embedding)
precision = ragas.metrics.collections.ContextPrecisionWithReference(llm=llm)
recall = ragas.metrics.collections.ContextRecall(llm=llm)

question = "What is the rated power of HS-5102-12A1?"
answer = "1KW"
contexts = ["## Electrical Specification\nRated power 1KW/1.2KW"]
ground_truth = "1KW"

score_faithfulness = faithfulness.score(
    user_input=question,
    response=answer,
    retrieved_contexts=contexts,
)
score_relevancy = relevancy.score(
    user_input=question,
    response=answer,
)
score_precision = precision.score(
    user_input=question,
    retrieved_contexts=contexts,
    reference=ground_truth,
)
score_recall = recall.score(
    user_input=question,
    retrieved_contexts=contexts,
    reference=ground_truth,
)

print(f"faithfulness:      {score_faithfulness}")
print(f"answer_relevancy:  {score_relevancy}")
print(f"context_precision: {score_precision}")
print(f"context_recall:    {score_recall}")
