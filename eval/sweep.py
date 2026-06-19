import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import chromadb
from chromadb.utils import embedding_functions
from ingest_multi import load_pdf_with_pages, DOCUMENTS
from chunkers import recursive_chunk
from score import evaluate


CONFIGS = [
    {"chunk_size": 300, "overlap": 30},
    {"chunk_size": 500, "overlap": 50},
    {"chunk_size": 800, "overlap": 80},
    {"chunk_size": 1000, "overlap": 100},
]


def ingest_config(chunk_size, overlap, collection_name):
    """
    Re-ingest all documents using one chunk_size/overlap config
    into a temporary ChromaDB collection.
    """
    client = chromadb.PersistentClient(path="../db")

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # Delete old temp collection if it already exists
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=ef,
    )

    ids, docs, metas = [], [], []

    for source, path in DOCUMENTS.items():
        for page_num, page_text in load_pdf_with_pages("../data/history/ncert_history_ch01.pdf"):
            chunks = recursive_chunk(
                page_text,
                chunk_size=chunk_size,
                overlap=overlap,
            )

            for ci, chunk in enumerate(chunks):
                ids.append(f"{source}_p{page_num}_c{ci}")
                docs.append(chunk)
                metas.append({
                    "source": source,
                    "page": page_num,
                    "chunk_size": chunk_size,
                    "overlap": overlap,
                })

    print(f"Adding {len(docs)} chunks to {collection_name}...")
    collection.add(ids=ids, documents=docs, metadatas=metas)
    print(f"Stored {collection.count()} chunks")


def run_sweep():
    """
    Test every config:
    1. Ingest with that config
    2. Run evaluate(k=3)
    3. Print Hit Rate and MRR
    """
    results = []

    for cfg in CONFIGS:
        chunk_size = cfg["chunk_size"]
        overlap = cfg["overlap"]

        collection_name = f"tmp_{chunk_size}_{overlap}"

        print("\n" + "=" * 60)
        print(f"Testing config: chunk_size={chunk_size}, overlap={overlap}")
        print("=" * 60)

        ingest_config(
            chunk_size=chunk_size,
            overlap=overlap,
            collection_name=collection_name,
        )

        result = evaluate(k=3, collection_name=collection_name)

        results.append({
            "config": f"recursive, {chunk_size}/{overlap}",
            "hit_rate": result["hit_rate"],
            "mrr": result["mrr"],
        })

    print("\n" + "=" * 60)
    print("FINAL SWEEP RESULTS")
    print("=" * 60)

    for r in results:
        print(f"{r['config']}: Hit Rate@3={r['hit_rate']:.3f}, MRR={r['mrr']:.3f}")

    best = max(results, key=lambda x: (x["hit_rate"], x["mrr"]))

    print("\nBest config:")
    print(best)


if __name__ == "__main__":
    run_sweep()
