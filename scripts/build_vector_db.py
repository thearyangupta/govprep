import chromadb
from chromadb.utils import embedding_functions
from load_and_chunk import load_pdf, chunk_text

client = chromadb.PersistentClient(path="../db")

sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2")

collection = client.get_or_create_collection(name="ncert_history_ch01",embedding_function=sentence_transformer_ef,)

if collection.count() > 0:
    print(f"Collection has {collection.count()} chunks. Skipping ingestion.")
else:
    print("Loading and chunking PDF...")
    text = load_pdf("../data/ncert_history_ch01.pdf")
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    print(f"Created {len(chunks)} chunks")

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {"source": "ncert_history_ch01", "chunk_index": i}
        for i in range(len(chunks))
    ]
    print("Embedding and storing chunks...")
    collection.add(ids=ids, documents=chunks, metadatas=metadatas)
    print(f"Stored {collection.count()} chunks in DB")



print("\n" + "="*60)
print("QUERY TEST")
print("="*60)
queries = [
    "who is the president of india",
    "what is the capital of a state",
    "national symbols of india",
]
for query in queries:
    print(f"\nQuery: '{query}'")
    results = collection.query(query_texts=[query],n_results=3)
    for i, doc in enumerate(results['documents'][0]):
        distance = results['distances'][0][i]
        print(f"\n Result {i+1} (distance: {distance:.4f}):")
        print(f" {doc[:200]}...")