import chromadb
from chromadb.utils import embedding_functions

def get_collection():
    """Connect to existing ChromaDB and return the collection."""
    client = chromadb.PersistentClient(path="../db")
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    return client.get_or_create_collection(name="ncert_history_ch01",embedding_function=embedding_fn)


def retrieve(query, k=3):
    """
    Retrieve top-k most relevant chunks for a query.
    Returns: [{"text": ..., "distance": ..., "metadata": ...}, ...]
    """
    collection = get_collection()
    results = collection.query(query_texts=[query], n_results=k)
    # ChromaDB returns nested lists (one per query). We sent 1, so [0].
    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "distance": results["distances"][0][i],
            "metadata": results["metadatas"][0][i],
        })
    return chunks


def format_chunks_for_display(chunks):
    """Pretty-print chunks for human reading."""
    output = []
    for i, chunk in enumerate(chunks):
        output.append(f"--- Chunk {i+1} (dist: {chunk['distance']:.4f}) ---")
        output.append(chunk["text"])
        output.append("")
    return "\n".join(output)


if __name__ == "__main__":
    test_queries = [
        "who is the prime minister of india",
        "what is article 370",
        "fundamental rights in indian constitution",
        "indian economy GDP",
        "current affairs 2024",
    ]
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {query}")
        print('='*60)
        chunks = retrieve(query, k=3)
        print(format_chunks_for_display(chunks))

