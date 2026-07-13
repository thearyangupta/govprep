from retrieve_pgvector import retrieve
from full_text_search import full_text_search


def doc_key(doc):
    """Create a stable identity for each document chunk."""
    return f"{doc['source']}::p{doc['page']}::{doc['text'][:80]}"


def rrf(dense_ranked, sparse_ranked, k=60, top_k=4):
    scores = {}
    docs = {}

    for rank, doc in enumerate(dense_ranked, start=1):
        key = doc_key(doc)

        scores[key] = (
            scores.get(key, 0)
            + 1 / (k + rank)
        )

        docs[key] = doc

    for rank, doc in enumerate(sparse_ranked, start=1):
        key = doc_key(doc)

        scores[key] = (
            scores.get(key, 0)
            + 1 / (k + rank)
        )

        docs[key] = doc

    ranked_keys = sorted(
        scores.keys(),
        key=lambda key: scores[key],
        reverse=True,
    )

    results = []

    for key in ranked_keys[:top_k]:
        doc_copy = docs[key].copy()
        doc_copy["rrf_score"] = scores[key]
        results.append(doc_copy)

    return results


def hybrid_search(
    query,
    k=4,
    collection_name="govprep_multi",
):
    """
    Combine pgvector dense retrieval with PostgreSQL
    full-text retrieval using Reciprocal Rank Fusion.
    """

    dense_results = retrieve(
        query,
        k=k,
        collection_name=collection_name,
    )

    sparse_results = full_text_search(
        query,
        k=k,
    )

    return rrf(
        dense_ranked=dense_results,
        sparse_ranked=sparse_results,
        top_k=k,
    )


if __name__ == "__main__":
    tests = [
        "Article 21",
        "fundamental rights",
        "physical features of india",
    ]

    for query in tests:
        print(f"\n{'=' * 55}")
        print(f"QUERY: {query}")
        print(f"{'=' * 55}")

        for chunk in hybrid_search(query, k=3):
            print(
                f"[{chunk['source']} "
                f"p{chunk['page']} "
                f"rrf={chunk['rrf_score']:.5f}] "
                f"{chunk['text'][:120]}..."
            )