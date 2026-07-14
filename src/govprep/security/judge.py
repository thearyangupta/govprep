from govprep.generation.llm import call_llm

def judge_faithfulness(question, context, answer):
    prompt = f"""You are evaluating a RAG answer.

Question: {question}

Retrieved context:
{context}

Answer given:
{answer}

Is every claim in the answer supported by the context?

Score 1-5 (5 = fully supported, 1 = mostly made up).

Reply as:
SCORE: <n>
REASON: <one line>
"""

    return call_llm(prompt)