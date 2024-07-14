import sys
import textwrap
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain.chains.retrieval_qa.base import BaseRetrievalQA, RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.documents.base import Document
from langchain_google_genai import (
    GoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)


def create_vector_store(texts, embeddings):
    batch_size = 100
    vector_store = FAISS.from_documents(texts[:batch_size], embeddings)

    for i in range(batch_size, len(texts), batch_size):
        vector_store.add_documents(texts[i : i + batch_size])
    return vector_store


def get_retrieval_qa_chain(
    documents: List[Document],
    *,
    llm_model_name: str = "gemini-1.5-flash-latest",
    max_retries: int = 6,
) -> BaseRetrievalQA:
    """
    Get a retrieval QA chain for interacting with the provided documents.

    Args
    ----
    documents (List[Document]): List of documents to interact with.

    Returns
    -------
    BaseRetrievalQA
        Retrieval QA chain for interacting with the provided documents.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200
    )

    texts = text_splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        task_type=None,
        client=None,
        google_api_key=None,
        transport=None,
        client_options=None,
        request_options=None,
    )

    vector_store = create_vector_store(texts, embeddings)

    retrieval_engine = vector_store.as_retriever(search_kwargs={"k": 3})

    qa_chain_openai = RetrievalQA.from_chain_type(
        llm=GoogleGenerativeAI(
            model=llm_model_name,
            client_options=None,
            transport=None,
            additional_headers=None,
            client=None,
            max_retries=max_retries,
        ),
        chain_type="stuff",
        retriever=retrieval_engine,
        return_source_documents=True,
    )

    return qa_chain_openai


def wrap_text_preserve_newlines(text: str, width: int = 110) -> str:
    lines = text.split("\n")

    # Wrap each line individually
    wrapped_lines = [textwrap.fill(line, width=width) for line in lines]

    # Join the wrapped lines back together using newline characters
    wrapped_text = "\n".join(wrapped_lines)

    return wrapped_text


def process_llm_response(llm_response: Dict[str, Any]) -> None:
    print(wrap_text_preserve_newlines(llm_response["result"]))
    print("\nSources:")
    for source in llm_response["source_documents"]:
        print(source.metadata["source"])


def execute_query(
    qa_chain_openai: BaseRetrievalQA, query: str
) -> Dict[str, Any]:
    chain_type_kwargs = {"query": query}
    llm_response = qa_chain_openai.invoke(chain_type_kwargs)
    return llm_response


def main() -> int:
    load_dotenv()

    loader = PyPDFDirectoryLoader(r"data\os", glob="./*.pdf")
    documents = loader.load()

    qa_chain_openai = get_retrieval_qa_chain(documents)

    query = """
Answer the following multiple choice question:

Question 7: What are the limitations of simulations in evaluating real-time
scheduling performance?
Multiple choice answers: A) Simulations cannot accurately model the real-time
constraints of the system.
B) Simulations are limited in their ability to capture the dynamic nature of
real-time workloads.
C) Simulations may not fully account for the impact of hardware resources on
scheduling performance.
D) Simulations can be time-consuming and expensive to develop and run.
E) Simulations may not accurately reflect the interactions between different
real-time tasks.
"""

    llm_response = execute_query(qa_chain_openai, query)
    process_llm_response(llm_response)
    return 0


if __name__ == "__main__":
    sys.exit(main())
