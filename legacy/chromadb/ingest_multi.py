import os
from pathlib import Path
from pypdf import PdfReader

def load_pdf_with_pages(filepath):
    """Return list of (page_number, page_text) tuples."""
    reader = PdfReader(filepath)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages.append((i + 1, text))
    return pages

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + chunk_size])
        start += chunk_size - overlap
    return chunks

# Map each source to the actual data subfolder containing PDFs
BASE_DIR = Path(__file__).resolve().parent.parent / "data"
DOCUMENTS = {
    "polity": BASE_DIR / "polity",
    "history": BASE_DIR / "history",
    "geography": BASE_DIR / "geography",
}

import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="../db")
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
collection = client.get_or_create_collection(
    name="govprep_multi", embedding_function=ef
)

if collection.count() == 0:
    ids, docs, metas = [], [], []
    for source, folder in DOCUMENTS.items():
        for pdf_path in sorted(folder.glob("*.pdf")):
            for page_num, page_text in load_pdf_with_pages(pdf_path):
                for ci, chunk in enumerate(chunk_text(page_text)):
                    ids.append(f"{source}_{pdf_path.stem}_p{page_num}_c{ci}")
                    docs.append(chunk)
                    metas.append({"source": source, "page": page_num, "file": pdf_path.name})
    print(f"Adding {len(docs)} chunks from {len(DOCUMENTS)} sources...")
    collection.add(ids=ids, documents=docs, metadatas=metas)
    print(f"Stored {collection.count()} chunks")
else:
    print(f"Already has {collection.count()} chunks")