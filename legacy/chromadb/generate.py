import os
from dotenv import load_dotenv
from google import genai
from legacy.chromadb.retrieve import retrieve

# Load API key
load_dotenv("../../.env") # .env is in python-fundamentals/ root
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are a UPSC CDS exam preparation assistant. You help \
students understand topics from previous year question papers.

CRITICAL RULES:
1. Answer using ONLY the passages provided below.
2. If passages don't contain enough info, say:
 "I don't have enough information in the provided passages."
3. Do NOT use your general knowledge - stay grounded in the passages.
4. Quote relevant lines when helpful.
5. Be concise but complete. 2-4 sentences usually.
6. Cite passages as [Passage 1], [Passage 2], etc.
"""

def build_prompt(query, chunks):
    """Combine the user query with retrieved chunks into a single prompt."""
    passages_text = ""

    for i, chunk in enumerate(chunks):
        passages_text += f"\n[Passage {i+1}]\n{chunk['text']}\n"

    full_prompt = f"""{SYSTEM_PROMPT}

PASSAGES FROM CDS PAPER:
{passages_text}

USER QUESTION: {query}

ANSWER:"""

    return full_prompt


def answer_with_rag(query, k=3):
    """
    Full RAG pipeline:
    1. Retrieve top-k relevant chunks
    2. Build prompt with chunks
    3. Call Gemini
    4. Return answer + the chunks used
    """
    chunks = retrieve(query, k=k)
    prompt = build_prompt(query, chunks)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return {
        "query": query,
        "answer": response.text,
        "chunks_used": chunks,
    }


if __name__ == "__main__":
    # Include queries that should fail (not in PDF) to test refusal
    test_queries = [
        "who is the prime minister of india", # likely in paper
        "what are fundamental rights", # likely in paper
        "explain article 370", # may or may not be
        "what is the price of pizza in mumbai", # NOT in paper
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {query}")
        print('='*60)

        result = answer_with_rag(query, k=3)

        print(f"\nANSWER:\n{result['answer']}")
        print(f"\n[Chunks: {len(result['chunks_used'])}, "
              f"top dist: {result['chunks_used'][0]['distance']:.4f}]")