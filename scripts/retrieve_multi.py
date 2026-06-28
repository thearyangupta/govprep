import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

def get_collection(collection_name="govprep_multi"):
   DB_PATH = Path(__file__).resolve().parent.parent / "db"
   client = chromadb.PersistentClient(path=str(DB_PATH))
   ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
   return client.get_or_create_collection(name=collection_name, embedding_function=ef)


def retrieve(query, k=4, source=None, collection_name="govprep_multi"):
 """Retrieve top-k chunks. Optionally filter to one source."""
 collection = get_collection(collection_name=collection_name)
 where = {"source": source} if source else None
 results = collection.query(
    query_texts=[query], n_results=k, where=where
 )
 chunks = []
 for i in range(len(results["documents"][0])):
    chunks.append({
        "text": results["documents"][0][i],
        "source": results["metadatas"][0][i]["source"], #Give me value of key "source"
        "page": results["metadatas"][0][i]["page"], #Give me the value stored under page
        "distance": results["distances"][0][i],
 })
 return chunks

if __name__ == "__main__": #This is the main block.
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
