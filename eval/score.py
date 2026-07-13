import json
import sys
from pathlib import Path
from typing import Callable


# Allow files inside eval/ to import modules from scripts/.
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


from retrieve_multi import retrieve as retrieve_chroma
from retrieve_pgvector import retrieve as retrieve_pgvector
from pg_hybrid_search import hybrid_search as pg_hybrid_search


Retriever = Callable[..., list[dict]]


def load_gold() -> list[dict]:
    """Load evaluation questions from gold_set.json."""
    gold_path = Path(__file__).resolve().parent / "gold_set.json"

    with open(gold_path, encoding="utf-8") as file:
        return json.load(file)


def get_vector_retriever(store: str) -> Retriever:
    """
    Return the retriever belonging to the requested vector store.
    """

    if store == "chroma":
        return retrieve_chroma

    if store == "pgvector":
        return retrieve_pgvector

    raise ValueError(
        "store must be either 'chroma' or 'pgvector'"
    )


def get_chunks(
    question: str,
    mode: str = "vector",
    store: str = "chroma",
    k: int = 3,
    collection_name: str = "govprep_multi",
) -> list[dict]:

    if mode == "vector":
        retriever = get_vector_retriever(store)

        return retriever(
            question,
            k=k,
            collection_name=collection_name,
        )

    if mode == "hybrid":
        return pg_hybrid_search(
            question,
            k=k,
            collection_name=collection_name,
        )

    raise ValueError(
        "mode must be either 'vector' or 'hybrid'"
    )


def hit_and_rank(
    gold_item: dict,
    mode: str = "vector",
    store: str = "chroma",
    k: int = 3,
    collection_name: str = "govprep_multi",
) -> tuple[bool, int | None]:
    """
    Return whether the required keyword was found and its rank.
    """

    chunks = get_chunks(
        question=gold_item["question"],
        mode=mode,
        store=store,
        k=k,
        collection_name=collection_name,
    )

    required_keyword = gold_item["required_keyword"].lower()

    for rank, chunk in enumerate(chunks, start=1):
        chunk_text = chunk["text"].lower()

        if required_keyword in chunk_text:
            return True, rank

    return False, None


def evaluate(
    mode: str = "vector",
    store: str = "chroma",
    k: int = 3,
    collection_name: str = "govprep_multi",
) -> dict:
    """
    Evaluate one retrieval configuration using Hit Rate and MRR.
    """

    gold = load_gold()

    hits = 0
    reciprocal_ranks = []

    label = store if mode == "vector" else "hybrid"

    print(f"\nMode: {mode}")
    print(f"Store: {label}")
    print(f"Top K: {k}")
    print("-" * 50)

    for item in gold:
        hit, rank = hit_and_rank(
            gold_item=item,
            mode=mode,
            store=store,
            k=k,
            collection_name=collection_name,
        )

        if hit:
            hits += 1
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)

        status = f"hit@{rank}" if hit else "MISS"

        print(
            f"[{status:>6}] "
            f"{item['question'][:55]}"
        )

    total_questions = len(gold)
    hit_rate = hits / total_questions
    mrr = sum(reciprocal_ranks) / total_questions

    print(f"\n{'=' * 50}")
    print(f"Mode: {mode}")
    print(f"Store: {label}")
    print(
        f"Hit Rate @{k}: "
        f"{hit_rate:.3f} ({hits}/{total_questions})"
    )
    print(f"MRR: {mrr:.3f}")

    return {
        "mode": mode,
        "store": label,
        "hit_rate": hit_rate,
        "mrr": mrr,
        "k": k,
    }


def print_parity_summary(
    chroma_result: dict,
    pgvector_result: dict,
) -> None:
    """Print ChromaDB and pgvector results side by side."""

    print("\n")
    print("=" * 62)
    print("CHROMA VS PGVECTOR PARITY")
    print("=" * 62)

    print(
        f"{'Store':<15}"
        f"{'Hit Rate@3':<18}"
        f"{'MRR':<12}"
    )

    print("-" * 62)

    print(
        f"{'ChromaDB':<15}"
        f"{chroma_result['hit_rate']:<18.3f}"
        f"{chroma_result['mrr']:<12.3f}"
    )

    print(
        f"{'pgvector':<15}"
        f"{pgvector_result['hit_rate']:<18.3f}"
        f"{pgvector_result['mrr']:<12.3f}"
    )

    hit_rate_difference = abs(
        chroma_result["hit_rate"]
        - pgvector_result["hit_rate"]
    )

    mrr_difference = abs(
        chroma_result["mrr"]
        - pgvector_result["mrr"]
    )

    print("-" * 62)
    print(
        f"Hit-rate difference: "
        f"{hit_rate_difference:.3f}"
    )
    print(f"MRR difference: {mrr_difference:.3f}")

    if hit_rate_difference == 0 and mrr_difference == 0:
        print("Result: Exact retrieval-metric parity confirmed.")
    else:
        print(
            "Result: Metrics differ. Compare question-level "
            "rankings before continuing."
        )


if __name__ == "__main__":
    chroma_results = evaluate(
        mode="vector",
        store="chroma",
        k=3,
    )

    pgvector_results = evaluate(
        mode="vector",
        store="pgvector",
        k=3,
    )

    print_parity_summary(
        chroma_result=chroma_results,
        pgvector_result=pgvector_results,
    )

    pg_hybrid_results = evaluate(
        mode="hybrid",
        store="pgvector",
        k=3,
    )