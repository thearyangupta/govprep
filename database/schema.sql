CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunks (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    subject TEXT,
    source TEXT,
    metadata JSONB,
    embedding VECTOR(384)
);

ALTER TABLE chunks
ADD COLUMN IF NOT EXISTS ts tsvector
GENERATED ALWAYS AS (
    to_tsvector('english', content)
) STORED;