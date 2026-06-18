import chromadb
from chromadb.utils import embedding_functions
from ingest_multi import load_pdf_with_pages, DOCUMENTS
from chunkers import recursive_chunk

client = chromadb.PersistentClient(path="../db")

ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="govprep_v2",
    embedding_function=ef
)

if collection.count() == 0:
    ids, docs, metas = [], [], []

    for source, folder in DOCUMENTS.items():
        for pdf_path in sorted(folder.glob("*.pdf")):
            for page_num, page_text in load_pdf_with_pages(pdf_path):
                for ci, chunk in enumerate(recursive_chunk(page_text)):
                    ids.append(f"{source}_{pdf_path.stem}_p{page_num}_c{ci}")
                    docs.append(chunk)
                    metas.append({"source": source, "page": page_num, "file": pdf_path.name})

    print(f"Adding {len(docs)} chunks from {len(DOCUMENTS)} sources...")
    collection.add(ids=ids, documents=docs, metadatas=metas)
    print(f"Stored {collection.count()} chunks")
else:
    print(f"Already has {collection.count()} chunks")