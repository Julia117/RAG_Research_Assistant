import sqlite3
from papers import pdf_extractor as pdf

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

EMBEDDER = "all-MiniLM-L6-v2"


def build_fulltext_chroma(db_name="arxiv_papers.db", persist_dir="chroma_arxiv_fulltext", max_docs=50):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, title, pdf_url FROM papers WHERE rowid IN ( \
        SELECT rowid FROM papers ORDER BY rowid DESC LIMIT {max_docs}\
    )\
    ORDER BY rowid DESC LIMIT {max_docs}")
    rows = cursor.fetchall()
    conn.close()

    all_texts = []
    all_metadatas = []

    for i, (pid, title, pdf_url) in enumerate(rows):
        print(f"\n[{i + 1}] Processing: {title}")
        try:
            full_text = pdf.extract_clean_text(pdf_url)
        except:
            continue

        if not full_text or len(full_text) < 500:
            print("Skipping (too short or failed)")
            continue

        chunks = pdf.chunk_text(full_text)
        for j, chunk in enumerate(chunks):
            all_texts.append(chunk)
            all_metadatas.append({
                "paper_id": pid,
                "title": title,
                "chunk_index": j,
                "pdf_url": pdf_url
            })

    print(f"\nEmbedding {len(all_texts)} chunks...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDER)

    vectordb = Chroma.from_texts(
        texts=all_texts,
        embedding=embeddings,
        metadatas=all_metadatas,
        collection_name="cs.CL",
        persist_directory=persist_dir
    )
    print(f"Papers were saved to: {persist_dir}")
    return vectordb


def test_fulltext_retrieval(vectordb, query="methods for retrieval-augmented generation"):
    results = vectordb.similarity_search(query, k=3)
    for i, r in enumerate(results, 1):
        print(f"\n Result {i}: {r.metadata['title']}")
        print(f"Chunk #{r.metadata['chunk_index']}  |  URL: {r.metadata['pdf_url']}")
        print(f"Excerpt:\n{r.page_content[:500]}...")


def load_chroma_db(persist_dir="chroma_arxiv_fulltext", collection_name="cs.CL"):
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDER)
    vectordb = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
        collection_name=collection_name
    )
    return vectordb
