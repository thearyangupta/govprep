from legacy.chromadb.retrieve_multi import retrieve
from legacy.chromadb.bm25_search import bm25_search


def doc_key(doc):  #create a unique identity for each document/chunk.
    return f"{doc['source']}::p{doc['page']}::{doc['text'][:80]}"


def rrf(dense_ranked, bm25_ranked, k=60, top_k=4):
    scores = {}
    docs = {}

    for rank, doc in enumerate(dense_ranked, start=1):
        key = doc_key(doc)
        scores[key] = scores.get(key, 0) + 1 / (k + rank)
        docs[key] = doc

    for rank, doc in enumerate(bm25_ranked, start=1):
        key = doc_key(doc)
        scores[key] = scores.get(key, 0) + 1 / (k + rank)
        docs[key] = doc

    ranked_keys = sorted(
        scores.keys(),
        key=lambda key: scores[key],
        reverse=True
    )

    results = []

    for key in ranked_keys[:top_k]:
        doc_copy = docs[key].copy()
        doc_copy["rrf_score"] = scores[key]
        results.append(doc_copy)

    return results


def hybrid_search(query, k=4, collection_name="govprep_multi"):
    dense_results = retrieve(
        query,
        k=k,
        collection_name=collection_name
    )

    bm25_results = bm25_search(
        query,
        k=k,
        collection_name=collection_name
    )

    return rrf(
        dense_ranked=dense_results,
        bm25_ranked=bm25_results,
        top_k=k
    )


if __name__ == "__main__":
    tests = [
        "Article 21",
        "fundamental rights",
        "physical features of india",
    ]

    for q in tests:
        print(f"\n{'='*55}\nQUERY: {q}\n{'='*55}")

        for c in hybrid_search(q, k=3):
            print(
                f"[{c['source']} p{c['page']} "
                f"rrf={c['rrf_score']:.5f}] {c['text'][:120]}..."
            )