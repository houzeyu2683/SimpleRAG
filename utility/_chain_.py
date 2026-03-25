"""
_chain_.py — RAG chain (LLM + LCEL)
"""

import os
import dotenv
import langchain_groq
import langchain_ollama
import langchain_core.prompts
import langchain_core.output_parsers
import langchain_core.runnables

dotenv.load_dotenv()

def getContent(documents: list) -> str:
    return ("\n\n".join(document.page_content for document in documents))


def getChain(retriever: object, configuration: dict) -> object:
    provider = configuration.get("llm_provider", "groq")
    model = configuration.get("llm_model", "llama-3.1-8b-instant")
    version = configuration.get("prompt_version", "baseline")
    template = configuration["prompts"][version]

    if provider == "ollama":
        llm = langchain_ollama.ChatOllama(model=model, temperature=0)
    else:
        llm = langchain_groq.ChatGroq(
            model=model,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0,
        )

    prompt = langchain_core.prompts.PromptTemplate.from_template(template)

    chain = (
        {"context": retriever | getContent, "question": langchain_core.runnables.RunnablePassthrough()}
        | prompt
        | llm
        | langchain_core.output_parsers.StrOutputParser()
    )

    return (chain)
