import json
from pathlib import Path
from typing import Callable

from govprep.retrieval.full_text_search import full_text_search
from govprep.retrieval.pg_hybrid_search import hybrid_search
from govprep.retrieval.retrieve_pgvector import retrieve


Retriever = Callable[..., list[dict]]

EVAL_DIR = Path(__file__).resolve().parent
GOLD_SET_PATH = EVAL_DIR / "gold_set.json"


def load_gold_set() -> list[dict]:
    """
    Load retrieval evaluation questions from gold_set.json.
    """

    with GOLD_SET_PATH.open(encoding="utf-8") as file:
        gold_set = json.load(file)

    if not isinstance(gold_set, list):
        raise ValueError(
            "gold_set.json must contain a JSON list."
        )

    return gold_set


def get_retriever(mode: str) -> Retriever:
    """
    Return the retrieval function for the selected mode.
    """

    retrievers = {
        "dense": retrieve,
        "sparse": full_text_search,
        "hybrid": hybrid_search,
    }

    try:
        return retrievers[mode]
    except KeyError as error:
        supported_modes = ", ".join(retrievers)

        raise ValueError(
            f"Unsupported mode '{mode}'. "
            f"Choose one of: {supported_modes}."
        ) from error


def get_chunks(
    question: str,
    mode: str,
    k: int = 3,
) -> list[dict]:
    """
    Retrieve the top-k chunks using the selected mode.
    """

    retriever = get_retriever(mode)

    return retriever(
        question,
        k=k,
    )


def find_keyword_rank(
    chunks: list[dict],
    required_keyword: str,
) -> int | None:
    """
    Return the rank of the first chunk containing the required
    keyword.

    Return None when none of the retrieved chunks contain it.
    """

    normalized_keyword = required_keyword.casefold()

    for rank, chunk in enumerate(chunks, start=1):
        chunk_text = chunk.get("text", "").casefold()

        if normalized_keyword in chunk_text:
            return rank

    return None


def evaluate_question(
    gold_item: dict,
    mode: str,
    k: int = 3,
) -> dict:
    """
    Evaluate one question against one retrieval mode.
    """

    question = gold_item["question"]
    required_keyword = gold_item["required_keyword"]

    chunks = get_chunks(
        question=question,
        mode=mode,
        k=k,
    )

    rank = find_keyword_rank(
        chunks=chunks,
        required_keyword=required_keyword,
    )

    hit = rank is not None
    reciprocal_rank = 1.0 / rank if rank else 0.0

    return {
        "question": question,
        "required_keyword": required_keyword,
        "hit": hit,
        "rank": rank,
        "reciprocal_rank": reciprocal_rank,
        "retrieved_chunks": chunks,
    }


def evaluate(
    mode: str,
    k: int = 3,
) -> dict:
    """
    Evaluate one retrieval mode using Hit Rate and MRR.
    """

    gold_set = load_gold_set()
    question_results = []

    print()
    print("=" * 68)
    print(f"RETRIEVAL MODE: {mode.upper()}")
    print(f"TOP K: {k}")
    print("=" * 68)

    for gold_item in gold_set:
        result = evaluate_question(
            gold_item=gold_item,
            mode=mode,
            k=k,
        )

        question_results.append(result)

        if result["hit"]:
            status = f"hit@{result['rank']}"
        else:
            status = "MISS"

        print(
            f"[{status:>6}] "
            f"{result['question'][:55]}"
        )

    total_questions = len(question_results)

    if total_questions == 0:
        raise ValueError(
            "The gold set contains no evaluation questions."
        )

    total_hits = sum(
        1
        for result in question_results
        if result["hit"]
    )

    reciprocal_rank_sum = sum(
        result["reciprocal_rank"]
        for result in question_results
    )

    hit_rate = total_hits / total_questions
    mrr = reciprocal_rank_sum / total_questions

    summary = {
        "mode": mode,
        "k": k,
        "total_questions": total_questions,
        "total_hits": total_hits,
        "hit_rate": hit_rate,
        "mrr": mrr,
        "questions": question_results,
    }

    print("-" * 68)
    print(
        f"Hit Rate@{k}: "
        f"{hit_rate:.3f} "
        f"({total_hits}/{total_questions})"
    )
    print(f"MRR:        {mrr:.3f}")

    return summary


def print_comparison(results: list[dict]) -> None:
    """
    Print retrieval results side by side.
    """

    print()
    print("=" * 68)
    print("RETRIEVAL COMPARISON")
    print("=" * 68)

    print(
        f"{'Mode':<15}"
        f"{'Hit Rate':<18}"
        f"{'MRR':<12}"
        f"{'Hits':<12}"
    )

    print("-" * 68)

    for result in results:
        hits = (
            f"{result['total_hits']}/"
            f"{result['total_questions']}"
        )

        print(
            f"{result['mode']:<15}"
            f"{result['hit_rate']:<18.3f}"
            f"{result['mrr']:<12.3f}"
            f"{hits:<12}"
        )


def main() -> None:
    """
    Run dense, sparse, and hybrid retrieval evaluation.
    """

    modes = [
        "dense",
        "sparse",
        "hybrid",
    ]

    results = [
        evaluate(
            mode=mode,
            k=3,
        )
        for mode in modes
    ]

    print_comparison(results)


if __name__ == "__main__":
    main()