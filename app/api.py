import logging
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from govprep.agent.agent import answer_agentic
from govprep.database.db import get_connection
from govprep.generation.memory import ConversationMemory
from govprep.generation.rag import answer


app = FastAPI(title="GovPrep API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

memory = ConversationMemory()

# Use Uvicorn's configured logger so logs appear properly in Cloud Run.
logger = logging.getLogger("uvicorn.error")


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


class HealthResponse(BaseModel):
    status: str
    database: str


@app.get("/health", response_model=HealthResponse)
def health():
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

    except Exception:
        logger.exception("Database health check failed")

        raise HTTPException(
            status_code=503,
            detail="Database is unreachable",
        )

    return HealthResponse(
        status="ok",
        database="reachable",
    )


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question is empty",
        )

    try:
        result = answer(req.question, memory)

    except HTTPException:
        raise

    except Exception:
        logger.exception("Unexpected chat request failure")

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while processing your question.",
        )

    return ChatResponse(
        answer=result["answer"],
        rewritten=result["rewritten"],
        sources=[
            Source(
                source=chunk["source"],
                page=chunk["page"],
            )
            for chunk in result["chunks"]
        ],
    )


@app.post("/chat/agent", response_model=AgentResponse)
def chat_agent(req: ChatRequest):
    if not req.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question is empty",
        )

    try:
        agent_answer = answer_agentic(req.question)

    except HTTPException:
        raise

    except Exception:
        logger.exception("Unexpected agent request failure")

        raise HTTPException(
            status_code=500,
            detail="The agent could not process the request.",
        )

    return AgentResponse(
        answer=agent_answer,
        mode="agentic",
    )