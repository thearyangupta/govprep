from src.govprep.retrieval.pg_hybrid_search import hybrid_search


def search(query: str, k: int = 4):
    """
    Search the active GovPrep knowledge base.

    The current implementation uses PostgreSQL hybrid retrieval:
    - PGVector dense search
    - PostgreSQL full-text search
    - Reciprocal Rank Fusion
    """
    return hybrid_search(
        query=query,
        k=k,
    )