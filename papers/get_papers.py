import requests
import feedparser
from langchain_groq import ChatGroq
from urllib3.exceptions import ReadTimeoutError
import time
import re


def get_category_id(category_name):
    llm_model = "llama-3.1-8b-instant"
    # llm_model = "openai/gpt-oss-120b"
    llm = ChatGroq(temperature=0.0, model=llm_model)
    reply = llm.invoke(f"On arxiv.org what is the category id for {category_name}? Give a short answer")
    regex = r"\b([a-zA-Z]|\-)+\.[a-zA-Z]{2}\b"
    try:
        match = re.search(regex, reply.content).group(0)
    except:
        return None
    return match


def request_papers(url):
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, timeout=20)
            break
        except ReadTimeoutError as e:
            if attempt == max_attempts:
                raise
        time.sleep(2)

    if response.status_code != 200:
        raise Exception(f"Request failed: {response.status_code}")
    return response


def fetch_arxiv_papers(category_id, query, max_results=5):
    base_url = "https://export.arxiv.org/api/query?"
    query = query.replace(" ", "%20")
    search_query = f"search_query=cat:{category_id}"
    if query:
        search_query = search_query + f"+AND+{query}"
    url = f"{base_url}{search_query}&start=0&max_results={max_results}"
    print(url)

    response = request_papers(url)
    feed = feedparser.parse(response.text)

    papers = []
    for entry in feed.entries:
        paper = {
            "id": entry.get("id"),
            "title": entry.get("title", "").replace("\n", " ").strip(),
            "authors": [author.name for author in entry.authors],
            "summary": entry.get("summary", "").replace("\n", " ").strip(),
            "published": entry.get("published"),
            "updated": entry.get("updated"),
            "link": entry.get("link"),
            "pdf_url": next((link.href for link in entry.links if "pdf" in link.href), None),
            "category": entry.get("arxiv_primary_category", {}).get("term", None),
        }
        papers.append(paper)

    return papers


def get_arxiv_papers(topic_name, max_results=50):
    category_id = get_category_id(topic_name)
    print(category_id)
    papers = fetch_arxiv_papers(category_id=category_id, max_results=max_results, query=topic_name)
    return papers
