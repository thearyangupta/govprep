from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

from ragas_compat import install_ragas_vertexai_compat

install_ragas_vertexai_compat()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from ragas.dataset_schema import SingleTurnSample
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import AnswerRelevancy, Faithfulness

from govprep.generation.memory import ConversationMemory
from govprep.generation.rag import answer


QUESTION = "What are Fundamental Rights?"


def main() -> None:
    memory = ConversationMemory()

    result = answer(
        QUESTION,
        memory,
        k=3,
    )

    contexts = [
        chunk["text"]
        for chunk in result["chunks"]
    ]

    evaluator_llm = LangchainLLMWrapper(
        ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.environ["GEMINI_API_KEY"],
            temperature=0,
        )
    )

    embeddings = LangchainEmbeddingsWrapper(
        HuggingFaceEmbeddings(
            model_name=(
                "sentence-transformers/"
                "all-MiniLM-L6-v2"
            )
        )
    )

    sample = SingleTurnSample(
        user_input=QUESTION,
        response=result["answer"],
        retrieved_contexts=contexts,
    )

    faithfulness = Faithfulness(
        llm=evaluator_llm,
    ).single_turn_score(
        sample
    )

    answer_relevancy = AnswerRelevancy(
        llm=evaluator_llm,
        embeddings=embeddings,
        strictness=1,
    ).single_turn_score(
        sample
    )

    print("===== RAGAS RESULTS =====")
    print(
        "Faithfulness =",
        round(faithfulness, 3),
    )
    print(
        "Answer Relevancy =",
        round(answer_relevancy, 3),
    )


if __name__ == "__main__":
    main()
