import json
import yaml
import openai
import pandas
import langchain_huggingface
import langchain_chroma
import langchain_ollama
import langchain_core.prompts
import langchain_core.output_parsers
import langchain_core.runnables
import tqdm
import ragas.llms
import ragas.embeddings
import ragas.metrics.collections
import pathlib

class Evaluation:

    def __init__(self, schema: dict) -> None:
        self.schema = schema
        return

    def activateRetrieval(self) -> bool:
        embedding = langchain_huggingface.HuggingFaceEmbeddings(
            model_name='BAAI/bge-m3'
        )
        self.retrieval = langchain_chroma.Chroma(
            embedding_function=embedding,
            persist_directory=self.schema['database'],
        )
        # self.retrieval = store.as_retriever()
        return(True)

    def getContent(self, document: list) -> str:
        content = []
        for item in document:
            content += [getattr(item, 'page_content')]
            continue
        content = "\n\n".join(content)
        return(content)

    def getTemplate(self) -> dict:
        path = self.schema['prompt']
        with open(path, encoding='utf-8') as paper:
            archive = yaml.safe_load(paper)
            pass
        return(archive)

    def activateModel(self) -> bool:
        model = langchain_ollama.ChatOllama(
            model=self.schema['model'],
            temperature=0,
            num_predict=512,
        )
        self.model = model
        return(True)

    def activateCategory(self) -> bool:
        template = self.getTemplate()
        conversion = langchain_core.output_parsers.StrOutputParser()
        extraction = langchain_core.prompts.PromptTemplate.from_template(
            template['extraction']
        )
        self.category = extraction | self.model | conversion
        return(True)

    def activateChain(self) -> bool:
        template = self.getTemplate()
        conversion = langchain_core.output_parsers.StrOutputParser()
        # extraction = langchain_core.prompts.PromptTemplate.from_template(
        #     template['extraction']
        # )
        # self.extractor = extraction | self.model | conversion
        prompt = langchain_core.prompts.PromptTemplate.from_template(
            template['query']
        )
        context = {
            "context": self.retrieval.as_retriever() | self.getContent,
            "question": langchain_core.runnables.RunnablePassthrough()
        }
        self.chain = (
            context | prompt | self.model | conversion
        )
        return(True)

    def getSecret(self) -> dict:
        path = self.schema['secret']
        with open(path, encoding='utf-8') as paper:
            archive = yaml.safe_load(paper)
            pass
        secret = archive
        return (secret)

    def getExam(self) -> dict:
        path = self.schema['exam']
        with open(path, encoding='utf-8') as file:
            archive = json.load(file)
            pass
        exam = archive
        return(exam)

    def inferSummary(self, top: int) -> bool:
        exam = self.getExam()
        # chain = self.getChain()
        summary = []
        for query in tqdm.tqdm(exam):
            question = query['question']
            device = self.category.invoke({"question": question}).strip()
            print(f"[device] {device}")
            # if(device.lower() != 'none'):
            #     context = self.retrieval.similarity_search(
            #         question, 
            #         k=top, 
            #         filter={"source": {"$like": "%HS-5102-12A1%"}}
            #     )
            #     pass
            # else:
            #     context = self.retrieval.similarity_search(question, k=top)
            #     pass
            context = self.retrieval.similarity_search(question, k=top)
            context_length = sum(len(document.page_content) for document in context)
            print(f"[context chars] {context_length} | {question[:60]}")
            for index, document in enumerate(context):
                print(f"  [{index}] {document.page_content[:200]}")
                continue
            answer = self.chain.invoke(question)
            summary.append({
                "question": question,
                "ground_truth": query['ground_truth'],
                "answer": answer,
                "contexts": [document.page_content for document in context],
                "type": query['type'],
            })
            continue
        self.summary = summary
        return (True)

    def readSummary(self) -> bool:
        path = pathlib.Path(self.schema['database']) / 'summary.json'
        with open(path, 'r', encoding='utf-8') as paper:
            summary = json.load(paper)
            pass
        self.summary = summary
        return(True)

    def writeScore(self) -> bool:
        # secret = self.getSecret()
        # client = openai.AsyncOpenAI(
        #     api_key=secret['GROQ_API_KEY'],
        #     base_url="https://api.groq.com/openai/v1",
        # )
        # llm = ragas.llms.llm_factory(model="llama-3.1-8b-instant", client=client)
        client = openai.AsyncOpenAI(
            api_key="local",
            base_url="http://localhost:11434/v1",
        )
        judge = ragas.llms.llm_factory(model=self.schema['judge'], client=client)
        embedding = ragas.embeddings.HuggingFaceEmbeddings(
            model='BAAI/bge-m3', device='cpu'
        )
        faithfulness = self.metric.Faithfulness(llm=judge)
        relevancy = self.metric.AnswerRelevancy(llm=judge, embeddings=embedding)
        precision = self.metric.ContextPrecisionWithReference(llm=judge)
        recall = self.metric.ContextRecall(llm=judge)
        rows = []
        for item in tqdm.tqdm(self.summary):
            question = item["question"]
            answer = item["answer"]
            contexts = item["contexts"]
            ground_truth = item["ground_truth"]
            rows.append({
                "question":         question,
                "answer":           answer,
                "ground_truth":     ground_truth,
                "faithfulness":     faithfulness.score(user_input=question, response=answer, retrieved_contexts=contexts).value,
                "answer_relevancy": relevancy.score(user_input=question, response=answer).value,
                "context_precision": precision.score(user_input=question, retrieved_contexts=contexts, reference=ground_truth).value,
                "context_recall":   recall.score(user_input=question, retrieved_contexts=contexts, reference=ground_truth).value,
            })
            continue
        table = pandas.DataFrame(rows)
        column = [
            'faithfulness', 
            'answer_relevancy', 
            'context_precision', 
            'context_recall'
        ]
        score = table[column].mean()
        path = pathlib.Path(self.schema['database']) / 'score.csv'
        score.to_csv(path, index=False)
        return (True)

    def writeSummary(self) -> bool:
        path = self.schema['database'] + '/summary.json'
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(self.summary, file, ensure_ascii=False, indent=2)
            pass
        return (True)

    metric = ragas.metrics.collections
    pass
