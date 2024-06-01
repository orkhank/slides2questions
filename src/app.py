import os
import streamlit as st
import sys
from langchain_community.vectorstores.faiss import FAISS

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.document_loaders import PyPDFDirectoryLoader
from load_dotenv import load_dotenv

import textwrap

DATA_DIR = r"data\nlp_slides"


def wrap_text_preserve_newlines(text, width=110):
    # Split the input text into lines based on newline characters
    lines = text.split("\n")

    # Wrap each line individually
    wrapped_lines = [textwrap.fill(line, width=width) for line in lines]

    # Join the wrapped lines back together using newline characters
    wrapped_text = "\n".join(wrapped_lines)

    return wrapped_text


def process_llm_response(llm_response):
    st.write(wrap_text_preserve_newlines(llm_response["result"]))
    st.write("\nSources:")
    for source in llm_response["source_documents"]:
        st.write(source.metadata["source"])
    


def main():
    load_dotenv()

    split_texts = load_and_split_documents()

    st.toast(f"Split documents into {len(split_texts)} chunks")

    qa_chain_openai = create_qa_chain(split_texts)

    query = st.text_input("Enter your question here:")

    if st.button("Generate Answer"):
        with st.spinner("Generating Answer..."):
            llm_response = execute_question_generation(qa_chain_openai, query)
            process_llm_response(llm_response)

    return 0

def create_qa_chain(split_texts):
    with st.spinner("Generating Embeddings..."):
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            task_type=None,
            client=None,
            google_api_key=None,
            transport=None,
            client_options=None,
            request_options=None,
        )

        # create a database from the documents in batches of 100
        google_genai_embedd = generate_embeddings(split_texts, embeddings)

    retriever_google_genai = google_genai_embedd.as_retriever(search_kwargs={"k": 18})

    qa_chain_openai = RetrievalQA.from_chain_type(
        llm=GoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            client_options=None,
            transport=None,
            additional_headers=None,
            client=None,
        ),
        chain_type="stuff",
        retriever=retriever_google_genai,
        return_source_documents=True,
    )
    
    return qa_chain_openai

@st.cache_data()
def load_and_split_documents():
    loader = PyPDFDirectoryLoader(DATA_DIR, glob="./*.pdf")
    with st.spinner("Loading Documents..."):
        documents = loader.load()

    with st.expander("Documents"):
        paths = {os.path.basename(doc.metadata["source"]) for doc in documents}
        st.write(f"Fetched {len(paths)} documents:")
        for path in sorted(paths):
            st.markdown(f"- {path}")

    with st.spinner("Splitting Documents..."):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )

        texts = text_splitter.split_documents(documents)
    return texts


def generate_embeddings(texts, embeddings):
    batch_size = 100
    google_genai_embedd = FAISS.from_documents(texts[:batch_size], embeddings)

    for i in range(batch_size, len(texts), batch_size):
        google_genai_embedd.add_documents(texts[i : i + batch_size])
    return google_genai_embedd


def execute_question_generation(qa_chain_openai, query):
    chain_type_kwargs = {"query": query}
    llm_response = qa_chain_openai.invoke(chain_type_kwargs)
    return llm_response


if __name__ == "__main__":
    sys.exit(main())
