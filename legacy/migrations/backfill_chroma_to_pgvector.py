from psycopg.types.json import Jsonb
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from db import get_connection
from legacy.chromadb.retrieve_multi import get_collection


BATCH_SIZE = 100


def build_postgres_row(document,metadata,embedding):
    subject = metadata.get("source")
    source = metadata.get("file")

    clean_metadata = {
        key: value
        for key, value in metadata.items()
        if key not in {"source", "file"}
    }

    return (
        document,
        subject,
        source,
        Jsonb(clean_metadata),
        embedding,
    )


def backfill():
    collection = get_collection()

    total_records = collection.count()
    print("Chroma records:", total_records)

    data = collection.get(
        include=["documents", "metadatas", "embeddings"]
    )

    documents = data["documents"]
    metadatas = data["metadatas"]
    embeddings = data["embeddings"]

    if not (
        len(documents)
        == len(metadatas)
        == len(embeddings)
    ):
        raise ValueError("Chroma returned mismatched result lengths")

    with get_connection() as connection:
        with connection.cursor() as cursor:
            inserted = 0

            for start in range(0, total_records, BATCH_SIZE):
                end = min(start + BATCH_SIZE, total_records)

                batch_rows = [
                    build_postgres_row(
                        document=documents[index],
                        metadata=metadatas[index],
                        embedding=embeddings[index],
                    )
                    for index in range(start, end)
                ]

                cursor.executemany(
                    """
                    INSERT INTO chunks (
                        content,
                        subject,
                        source,
                        metadata,
                        embedding
                    )
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    batch_rows,
                )

                connection.commit()

                inserted += len(batch_rows)
                print(f"Inserted {inserted}/{total_records}")

    print("Backfill completed successfully.")


if __name__ == "__main__":
    backfill()