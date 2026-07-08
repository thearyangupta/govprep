import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from retrieve_multi import retrieve
from hybrid_search import hybrid_search


def load_gold():
    with open(Path(__file__).resolve().parent / "gold_set.json") as f:
        return json.load(f)


def get_chunks(question, mode="vector", k=3, collection_name="govprep_multi"):
    if mode == "vector":
        return retrieve(question, k=k, collection_name=collection_name)

    if mode == "hybrid":
        return hybrid_search(question, k=k)

    raise ValueError("mode must be either 'vector' or 'hybrid'")


def hit_and_rank(gold_item, mode="vector", k=3, collection_name="govprep_multi"):
    """Returns (hit:bool, rank:int or None) for one question."""
    chunks = get_chunks(
        gold_item["question"],
        mode=mode,
        k=k,
        collection_name=collection_name,
    )

    keyword = gold_item["required_keyword"].lower()

    for rank, c in enumerate(chunks, start=1):
        if keyword in c["text"].lower():
            return True, rank

    return False, None


def evaluate(mode="vector", k=3, collection_name="govprep_multi"):
    gold = load_gold()
    hits, reciprocal_ranks = 0, []

    print(f"\nMode: {mode}")
    print(f"Top K: {k}")
    print("-" * 50)

    for item in gold:
        hit, rank = hit_and_rank(
            item,
            mode=mode,
            k=k,
            collection_name=collection_name,
        )

        if hit:
            hits += 1
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)

        status = f"hit@{rank}" if hit else "MISS"
        print(f"[{status:>6}] {item['question'][:55]}")

    n = len(gold)
    hit_rate = hits / n
    mrr = sum(reciprocal_ranks) / n

    print(f"\n{'=' * 50}")
    print(f"Mode: {mode}")
    print(f"Hit Rate @{k}: {hit_rate:.3f} ({hits}/{n})")
    print(f"MRR: {mrr:.3f}")

    return {
        "mode": mode,
        "hit_rate": hit_rate,
        "mrr": mrr,
        "k": k,
    }


if __name__ == "__main__":
    evaluate(mode="vector", k=3)
    evaluate(mode="hybrid", k=3)