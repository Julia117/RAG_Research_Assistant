from papers import get_papers
from database import sqlite_conn
from prompt_toolkit import prompt
from database import chroma_conn as chroma
from retriever import retriever
from dotenv import load_dotenv
import logging

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
load_dotenv() 


def main():
    while True:
        print("Hello! \nThis project allows to fetch articles from arxive.org on a topic you're interested in and answer any questions you may have!" \
        "\nWe already have a small database with papers on Retrieval Augmented Generation. \n" \
        "Would you like to use it? Write \"yes\" if so, otherwise type the name of the topic you're interested in. Examples: Machine Learning, Proof Complexity, Medical Physics.")

        user_input = prompt(">>> ")
        if user_input.lower() == "yes":
            print("What is your question?")
            while True:
                user_input = prompt(">>> ")
                if user_input.lower() in ["exit", "quit"]:
                        break
                retriever.chat(user_input)


        elif user_input.lower() in ["exit", "quit"]:
            break

        else:
            topic_name = user_input
            print("And how many papers would you like to fetch?")
            user_input = prompt(">>> ")
            max_results = user_input
            papers = get_papers.get_arxiv_papers(topic_name, max_results)
            sqlite_conn.create_db(db_name='arxiv_papers.db')
            sqlite_conn.insert_papers(papers, db_name='arxiv_papers.db')
            print("Papers were successfully fetched and stored in SQLite.")
            vectordb = chroma.build_fulltext_chroma(max_docs=max_results)
            chroma.test_fulltext_retrieval(vectordb)
            print("What is your question?")
            while True:
                user_input = prompt(">>> ")
                if user_input.lower() in ["exit", "quit"]:
                        break
                retriever.chat(user_input)
             
            

if __name__ == "__main__":
    main()