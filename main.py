from fastapi import FastAPI, Request
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))

from memory import ConversationMemory
from generate_v1 import answer

app = FastAPI(title="govprep API")

# one shared memory for now
memory = ConversationMemory()


@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    question = data["question"]

    result = answer(question, memory)

    return {
        "answer": result["answer"],
        "rewritten": result["rewritten"],
        "sources": [
            {"source": c["source"], "page": c["page"]}
            for c in result["chunks"]
        ],
    }