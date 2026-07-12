import sys
sys.path.insert(0, ".")
from sentence_transformers import SentenceTransformer
from psycopg.types.json import Jsonb

from db import get_connection


model = SentenceTransformer("all-MiniLM-L6-v2")

content = (
    "Fundamental Rights are guaranteed under "
    "Part III of the Constitution."
)

embedding = model.encode(content).tolist()

metadata = {
    "page": 87,
    "chapter": "Fundamental Rights",
    "chunk_number": 14,
}


with get_connection() as connection:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO chunks (
                content,
                subject,
                source,
                metadata,
                embedding
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (
                content,
                "Polity",
                "ncert_polity.pdf",
                Jsonb(metadata),
                embedding,
            ),
        )

        inserted_id = cursor.fetchone()[0]
        print("Inserted row ID:", inserted_id)

query = "Which rights are protected by the Indian Constitution?"
query_embedding = model.encode(query).tolist()

with get_connection() as connection:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                content,
                source,
                metadata,
                embedding <=> %s AS distance
            FROM chunks
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> %s
            LIMIT 3;
            """,
            (
                query_embedding,
                query_embedding,
            ),
        )

        rows = cursor.fetchall()

        for row in rows:
            print()
            print("ID:", row[0])
            print("Content:", row[1])
            print("Source:", row[2])
            print("Metadata:", row[3])
            print("Distance:", row[4])