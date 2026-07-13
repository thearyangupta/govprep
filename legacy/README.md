# Legacy implementations

This directory preserves earlier GovPrep implementations and experiments.

- `chromadb/` — original ChromaDB retrieval and ingestion pipeline
- `agents/` — earlier custom LangGraph agent implementation
- `migrations/` — one-time ChromaDB-to-PGVector migration utilities
- `versions/` — earlier application versions
- `experiments/` — learning and development experiments

The active application uses PostgreSQL, PGVector, PostgreSQL full-text search,
and Reciprocal Rank Fusion under `src/govprep/`.