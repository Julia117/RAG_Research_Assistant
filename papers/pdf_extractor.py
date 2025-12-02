import pymupdf
import requests
from langchain_text_splitters import RecursiveCharacterTextSplitter
import io
import re


def extract_clean_text(pdf_path, min_font_size=7):
    response = requests.get(pdf_path, timeout=30)
    response.raise_for_status()
    pdf_stream = io.BytesIO(response.content)
    doc = pymupdf.open(stream=pdf_stream, filetype="pdf")
    
    text = ""
    cleaned_text = []

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            # Skip image blocks (plots, figures, tables)
            if "image" in b:
                continue

            for line in b.get("lines", []):
                for span in line["spans"]:
                    text = span["text"].strip()
                    if span["size"] < min_font_size:
                        continue
                    # Skip figure/table captions
                    if re.match(r"^(figure|fig\.|table)\b", text.lower()):
                        continue
                    cleaned_text.append(text)

    text = " ".join(cleaned_text)

    # Remove References section
    text = re.split(r"\b(references|bibliography)\b", text, flags=re.IGNORECASE)[0]

    # Fix hyphenated line breaks (e.g., "contribu- tion" → "contribution")
    text = re.sub(r"(\w+)-\s+(\w+)", r"\1\2", text)

    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)


    return text.strip()
    

def chunk_text(text, chunk_size=1000, overlap=100):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ".", " "]
    )
    return splitter.split_text(text)    