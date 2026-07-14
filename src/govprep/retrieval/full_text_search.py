from govprep.database.db import get_connection


def full_text_search(query, k=4, source=None):
    """
    Retrieve top-k chunks using PostgreSQL Full-Text Search.
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:

            if source:
                cursor.execute(
                    """
                    SELECT
                        content,
                        subject,
                        metadata,
                        ts_rank(
                            ts,
                            plainto_tsquery('english', %s)
                        ) AS score
                    FROM chunks
                    WHERE
                        subject = %s
                        AND ts @@ plainto_tsquery('english', %s)
                    ORDER BY score DESC
                    LIMIT %s;
                    """,
                    (
                        query,
                        source,
                        query,
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
                        ts_rank(
                            ts,
                            plainto_tsquery('english', %s)
                        ) AS score
                    FROM chunks
                    WHERE
                        ts @@ plainto_tsquery('english', %s)
                    ORDER BY score DESC
                    LIMIT %s;
                    """,
                    (
                        query,
                        query,
                        k,
                    ),
                )

            rows = cursor.fetchall()

    chunks = []

    for content, subject, metadata, score in rows:
        chunks.append(
            {
                "text": content,
                "source": subject,
                "page": metadata.get("page"),
                "score": float(score),
            }
        )

    return chunks


if __name__ == "__main__":

    tests = [
        "fundamental rights",
        "physical features of india",
        "ancient indian history",
    ]

    for query in tests:

        print("\n" + "=" * 60)
        print(query)
        print("=" * 60)

        results = full_text_search(query)

        for chunk in results:
            print(
                f"[{chunk['source']} "
                f"p{chunk['page']} "
                f"score={chunk['score']:.3f}]"
            )

            print(chunk["text"][:120])
            print()