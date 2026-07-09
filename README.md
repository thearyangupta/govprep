# govprep

An AI study assistant for Indian government exam aspirants (UPSC / CDS / SSC).
Ask a question in plain language and get a grounded, source-cited answer drawn
from NCERT study material — and a clear "not in my sources" when the answer
isn't there, instead of a hallucinated guess.

Built from scratch in native Python (no heavy frameworks in the core) to
understand each part of a retrieval-augmented generation (RAG) system, then
measured and tuned with a real evaluation loop rather than guesswork.

![govprep web UI](govprep-ai-ss-2.png)

## What it does

- Answers exam-prep questions grounded **only** in the source material
- Retrieves across **multiple subjects** and tells you which book + page each
  fact came from (source attribution)
- Remembers the conversation, so **follow-up questions work**
  ("what are their powers?" resolves correctly from context)
- **Refuses to answer** when the retrieved passages don't support it — reducing
  hallucination instead of making something up
- Runs as a **FastAPI backend** with a **Streamlit web frontend**, or from the
  command line
- Supports both a **fixed RAG pipeline** and an **agentic ReAct mode**
- Uses **hybrid retrieval (Dense + BM25 + Reciprocal Rank Fusion)** for improved document retrieval

## Architecture

                Streamlit frontend
                       │
                       ▼
                 FastAPI backend
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼

   Fixed RAG (/chat)          ReAct Agent (/chat/agent)

        │                             │
        └──────────────┬──────────────┘
                       ▼
       Hybrid Retrieval (Dense + BM25 + RRF)
                       ▼
                 Gemini 2.5 Flash
                       ▼
                 Source-cited Answer

The frontend and backend are separate services. The UI sends questions to the
API over HTTP and renders the response — it has no knowledge of how the answer
is produced. The backend owns the RAG pipeline and returns validated JSON.

## Current corpus

Currently indexed over **NCERT Class 11** textbooks (all chapters):

- **Political Science** — *Indian Constitution at Work*
- **History** — *Themes in World History*
- **Geography** — *Fundamentals of Physical Geography*

The corpus is **not fixed or limited to these PDFs** — the ingestion pipeline
loads any text-layer documents placed in the subject folders, so more subjects,
classes, and source types can be added over time. NCERT was chosen as the
starting corpus because it is core, well-structured study material for UPSC/CDS
General Studies.

## How it works

govprep has two pipelines:

**Ingestion (run once, ahead of time)**
```
PDFs  ->  text extraction  ->  chunking  ->  embeddings  ->  vector store
```

**Query (runs on every question)**
```
question + history
   -> rewrite question to be self-contained (resolves follow-ups)
   -> retrieve top-k relevant chunks across all subjects
   -> build a grounded prompt (history + passages + sources)
   -> generate answer, cited to source
   -> save the turn to memory
```

## ReAct Agent (LangGraph)

GovPrep now supports two answering modes.

- **/chat** — the original deterministic RAG pipeline.
- **/chat/agent** — a LangGraph-based ReAct agent.

The fixed pipeline always follows the same retrieval flow, while the agent reasons about the user's request, decides which tools to use, observes the results, and continues until it has enough information to answer.

## Available Tools

- `search_corpus()` — retrieves relevant NCERT passages with source attribution.
- `calculate()` — evaluates simple mathematical expressions.

## Reliability Features

- Multi-step reasoning (Thought → Action → Observation)
- Max-iteration safety to prevent infinite loops
- Graceful tool-failure handling (tool errors become observations)
- Reasoning trace visible for debugging
- Prompt injection resistance through explicit agent system prompt constraints
- Security testing against common prompt injection attacks

## Agent WorkFlow

```text
User → Agent → Tool (if needed) → Observation → Agent(Reason Again) → Final Answer
```

## API

The backend exposes a single chat endpoint.

```
POST /chat
  request:  { "question": "what are fundamental rights?" }
  response: { "answer": "...", "rewritten": "...",
              "sources": [ { "source": "polity", "page": 4 } ] }
```

Run the backend and open the auto-generated interactive docs at
http://127.0.0.1:8000/docs . Input is validated with Pydantic — malformed
requests return a clear `422`; errors return proper status codes (`400` for bad
input, `503` when the model is busy).

## Security

GovPrep was tested against common prompt injection attacks.

The fixed RAG pipeline successfully remained grounded in retrieved passages.

Testing revealed an instruction-override vulnerability in the initial agent implementation. The agent system prompt was strengthened with explicit security constraints to reject prompt injection attempts, prevent system prompt disclosure, and refuse requests to bypass retrieved sources.

The testing process and findings are documented in `SECURITY.md`.

## Tech stack

- **Python 3.11+**
- **FastAPI + Uvicorn** — backend API
- **Pydantic** — request/response validation
- **Streamlit** — web frontend
- **google-genai** SDK — Gemini 2.5 Flash (generation), Gemini 2.5 Flash-Lite
  (query rewriting)
- **ChromaDB** — local vector database
- **sentence-transformers** (`all-MiniLM-L6-v2`) — embeddings
- **pypdf** — document loading

## Retrieval evaluation

Retrieval quality was measured, not assumed. A 15-question gold set (across all
three subjects, each tagged with a required keyword and expected subject) is
scored with **Hit Rate@3** and **MRR**, counting a hit only when both the
correct keyword and correct subject appear.

| Config                          | Hit Rate@3 | MRR   |
|---------------------------------|------------|-------|
| Baseline (fixed 500-char)       | 0.533      | 0.433 |
| Tuned (recursive 1000/100, k=3) | 0.733      | 0.656 |
| Hybrid (Dense + BM25 + RRF)     | 0.458      | 0.410 |

The tuned vector pipeline achieved a **+37% Hit Rate / +52% MRR**
improvement over the baseline through chunking strategy, chunk size,
and top-k tuning.

Hybrid retrieval was evaluated using the same gold set to compare
Dense + BM25 + Reciprocal Rank Fusion against the tuned vector
baseline. Results are reported as measured on this corpus rather than
assuming hybrid search always performs better.

Full methodology, evaluation scripts, and experiment logs are available
in [EVALUATION.md](EVALUATION.md).

## Project structure

```
govprep/
  main.py                # FastAPI backend (POST /chat)
  app.py                 # Streamlit frontend (calls the API over HTTP)
  govprep_v1.py          # command-line interface
  scripts/
    ingest_v2.py         # ingestion: load PDFs, chunk, embed, store
    chunkers.py          # recursive chunking
    retrieve_multi.py    # multi-document retrieval with metadata
    memory.py            # conversation memory
    rewrite.py           # query rewriting for follow-ups
    generate_v1.py       # the query pipeline orchestrator
    llm.py               # centralized LLM calls with retry/backoff
    agent.py              # LangGraph ReAct agent
    hybrid_search.py      # Hybrid retrieval (Dense + BM25 + RRF)
    bm25_search.py        # BM25 retrieval
    rrf.py                # Reciprocal Rank Fusion
  eval/
    gold_set.json        # evaluation questions
    score.py             # Hit Rate@3 + MRR scorer
    sweep.py             # chunk-size sweep
    results.md           # raw experiment log
  data/
    polity/  history/  geography/   # NCERT PDFs (per subject)
  EVALUATION.md          # evaluation method + results + limitations
  README.md
  SECURITY.md           # Prompt injection testing and security notes
```

## Setup

```bash
# 1. clone and enter the repo
git clone https://github.com/thearyangupta/govprep.git
cd govprep

# 2. create + activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. install dependencies
pip install -r requirements.txt

# 4. add your Gemini API key
#    create a file named .env containing:
#    GEMINI_API_KEY=your_key_here

# 5. add source PDFs (text-layer) into data/polity, data/history, data/geography
```

## Usage

**Ingest the corpus** (run once, builds the vector store):
```bash
cd scripts
python ingest_v2.py recursive govprep_v2 1000 100
```

**Run the full app** (backend + frontend, in two terminals):
```bash
# terminal 1 — backend
uvicorn main:app --reload

# terminal 2 — frontend
streamlit run app.py
```

**Or use the command line:**
```bash
python govprep_v1.py
```

## Notes

- Source PDFs and the local vector store are not committed to the repo.
- Built as a learning project to understand production-grade RAG end to end: retrieval, hybrid search, evaluation, agentic workflows, prompt injection defense, grounding, and deployment.

---

