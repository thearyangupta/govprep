import chromadb
from chromadb.utils import embedding_functions

def get_collection():
 client = chromadb.PersistentClient(path="../db")
 ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
 return client.get_or_create_collection(name="govprep_v2", embedding_function=ef)


def retrieve(query, k=4, source=None):
 """Retrieve top-k chunks. Optionally filter to one source."""
 collection = get_collection()
 where = {"source": source} if source else None
 results = collection.query(
    query_texts=[query], n_results=k, where=where
 )
 chunks = []
 for i in range(len(results["documents"][0])):
    chunks.append({
        "text": results["documents"][0][i],
        "source": results["metadatas"][0][i]["source"],
        "page": results["metadatas"][0][i]["page"],
        "distance": results["distances"][0][i],
 })
 return chunks

if __name__ == "__main__":
 tests = [
 "what are fundamental rights", # expect: polity
 "physical features of india", # expect: geography
 "ancient indian history", # expect: history
 ]
 for q in tests:
    print(f"\n{'='*55}\nQUERY: {q}\n{'='*55}")
    for c in retrieve(q, k=3):
        print(f"[{c['source']} p{c['page']} "
              f"dist={c['distance']:.3f}] {c['text'][:120]}...")
