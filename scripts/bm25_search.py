import chromadb
from pathlib import Path
from rank_bm25 import BM25Okapi


def load_chunks(collection_name="govprep_multi"):
    DB_PATH = Path(__file__).resolve().parent.parent / "db"
    client = chromadb.PersistentClient(path=str(DB_PATH))

    collection = client.get_or_create_collection(name=collection_name)

    data = collection.get(include=["documents", "metadatas"])

    chunks = []

    for i in range(len(data["documents"])):
        chunks.append({
            "text": data["documents"][i],
            "source": data["metadatas"][i]["source"],
            "page": data["metadatas"][i]["page"],
        })

    return chunks


def tokenize(text):
    return text.lower().split()


def bm25_search(query, k=4, collection_name="govprep_multi"):
    chunks = load_chunks(collection_name=collection_name)

    if not chunks:
        return []

    tokenized_chunks = [
        tokenize(chunk["text"])
        for chunk in chunks
    ]

    bm25 = BM25Okapi(tokenized_chunks)

    tokenized_query = tokenize(query)

    scores = bm25.get_scores(tokenized_query)

    ranked_indexes = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )

    results = []

    for i in ranked_indexes[:k]:
        results.append({
            "text": chunks[i]["text"],
            "source": chunks[i]["source"],
            "page": chunks[i]["page"],
            "score": scores[i],
        })

    return results


if __name__ == "__main__":
    tests = [
        "Article 21",
        "fundamental rights",
        "physical features of india",
    ]

    for q in tests:
        print(f"\n{'='*55}\nQUERY: {q}\n{'='*55}")

        for c in bm25_search(q, k=3):
            print(
                f"[{c['source']} p{c['page']} "
                f"score={c['score']:.3f}] {c['text'][:120]}..."
            )