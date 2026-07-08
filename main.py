from fastapi import FastAPI, HTTPException
import sys
from pathlib import Path
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))

from memory import ConversationMemory
from generate_v1 import answer
from agent import answer_agentic

app = FastAPI(title="govprep API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

memory = ConversationMemory()


class ChatRequest(BaseModel):
    question: str


class Source(BaseModel):
    source: str
    page: int


class ChatResponse(BaseModel):
    answer: str
    rewritten: str
    sources: List[Source]


class AgentResponse(BaseModel):
    answer: str
    mode: str


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):

    if not req.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question is empty"
        )

    try:
        result = answer(req.question, memory)

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="The model is busy. Please try again."
        )

    return ChatResponse(
        answer=result["answer"],
        rewritten=result["rewritten"],
        sources=[
            Source(source=c["source"], page=c["page"])
            for c in result["chunks"]
        ],
    )


@app.post("/chat/agent", response_model=AgentResponse)
def chat_agent(req: ChatRequest):

    if not req.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question is empty"
        )

    try:
        agent_answer = answer_agentic(req.question)

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=str(e)
        )

    return AgentResponse(
        answer=agent_answer,
        mode="agentic"
    )