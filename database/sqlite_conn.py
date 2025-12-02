import sqlite3


def create_db(db_name="arxiv_papers.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            id TEXT PRIMARY KEY,
            title TEXT,
            authors TEXT,
            summary TEXT,
            published TEXT,
            updated TEXT,
            link TEXT,
            pdf_url TEXT,
            category TEXT
        )
    """)
    conn.commit()
    conn.close()


def insert_papers(papers, db_name="arxiv_papers.db"):

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    for paper in papers:
        cursor.execute("""
            INSERT OR REPLACE INTO papers 
            (id, title, authors, summary, published, updated, link, pdf_url, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            paper["id"],
            paper["title"],
            ", ".join(paper["authors"]),
            paper["summary"],
            paper["published"],
            paper["updated"],
            paper["link"],
            paper["pdf_url"],
            paper["category"]
        ))

    conn.commit()
    conn.close()    