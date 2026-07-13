from sentence_transformers import SentenceTransformer
from src.govprep.database.db import get_connection


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def retrieve(
    query,
    k=4,
    source=None,
    collection_name="govprep_multi",
):
    """
    Retrieve top-k chunks from PostgreSQL + pgvector.

    collection_name is retained temporarily so this function has
    the same interface as the existing Chroma retriever.
    """
    _ = collection_name

    query_embedding = model.encode(query)
    # The query embedding is passed twice because it is used
    # once to compute the distance and again for ORDER BY.
    with get_connection() as connection:
        with connection.cursor() as cursor:
            if source:
                cursor.execute(
                    """
                    SELECT
                        content,
                        subject,
                        metadata,
                        embedding <=> %s AS distance
                    FROM chunks
                    WHERE subject = %s
                      AND embedding IS NOT NULL
                    ORDER BY embedding <=> %s
                    LIMIT %s;
                    """,
                    (
                        query_embedding,
                        source,
                        query_embedding,
                        k,
                    ),
                )
            else:
                cursor.execute(
                    """
                    SELECT
                        content,
                        subject,
                        metadata,
                        embedding <=> %s AS distance
                    FROM chunks
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> %s
                    LIMIT %s;
                    """,
                    (
                        query_embedding,
                        query_embedding,
                        k,
                    ),
                )

            rows = cursor.fetchall()

    chunks = []

    for content, subject, metadata, distance in rows:
        chunks.append(
            {
                "text": content,
                "source": subject,
                "page": metadata.get("page"),
                "distance": float(distance),
            }
        )

    return chunks


if __name__ == "__main__":
    tests = [
        "what are fundamental rights",
        "physical features of india",
        "ancient indian history",
    ]

    for query in tests:
        print(f"\n{'=' * 55}")
        print(f"QUERY: {query}")
        print(f"{'=' * 55}")

        for chunk in retrieve(query, k=3):
            print(
                f"[{chunk['source']} "
                f"p{chunk['page']} "
                f"dist={chunk['distance']:.3f}] "
                f"{chunk['text'][:120]}..."
            )