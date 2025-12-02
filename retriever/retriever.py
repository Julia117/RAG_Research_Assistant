from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_community.document_compressors import FlashrankRerank

from database import chroma_conn
from groq import Groq
import os




def build_research_assistant(vectordb):
    retriever = vectordb.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 20}
    )

    # client = Groq(
    #     api_key=os.getenv("GROQ_API_KEY"), 
    # )
    llm = ChatGroq(
        # groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.0,
        model="llama-3.1-8b-instant"
    )

    prompt = PromptTemplate(
        input_variables=["context", "input"],
        template="""
            You are a precise assistant.

            Context:
            {context}

            Question:
            {input}

            Answer concisely:
            """
    )


    compressor = FlashrankRerank()
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, base_retriever=retriever)



    document_chain = create_stuff_documents_chain(llm, prompt)

    qa_chain = create_retrieval_chain(compression_retriever, document_chain)
    return qa_chain

def ask_question(qa_chain, query):
    print(f"\nQuestion: {query}\n")
    result = qa_chain.invoke({"input": query})
    
    print(" Answer:\n", result["answer"])
    print("\n Sources:")
    for doc in result["context"]:
        meta = doc.metadata
        print(f"- {meta['title']} (chunk {meta['chunk_index']}) → {meta['pdf_url']}")  


def chat(question):
    vectordb = chroma_conn.load_chroma_db()
    qa_chain = build_research_assistant(vectordb)
    ask_question(
        qa_chain, question
    )


# WORKING STUFF
def build_research_assistant_old(vectordb):
    retriever = vectordb.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    llm = ChatGroq(
        temperature=0.0,
        model="llama-3.1-8b-instant"
    )

    prompt = PromptTemplate(
        input_variables=["context", "input"],
        template="""
            You are a precise assistant. Always start with "hello!".

            Context:
            {context}

            Question:
            {input}

            Answer concisely:
            """
    )

    document_chain = create_stuff_documents_chain(llm, prompt)

    qa_chain = create_retrieval_chain(retriever, document_chain)
    return qa_chain

def chat_old(question):
    vectordb = chroma_conn.load_chroma_db()
    qa_chain = build_research_assistant_old(vectordb)
    ask_question(
        qa_chain, question
    )