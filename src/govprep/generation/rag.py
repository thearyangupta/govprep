import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from src.govprep.retrieval.search import search
from src.govprep.generation.rewrite import rewrite_query

env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
SYSTEM = """You are a UPSC/CDS exam prep assistant answering from \
NCERT textbooks. Rules:
1. Answer ONLY from the passages below.
2. If the passages don't contain the answer, say "I don't have \
 that in my sources."
3. Cite the source of each fact like [polity] or [history].
4. Use the conversation history for context, but base facts on passages.
5. Be concise - 2-4 sentences."""
def build_prompt(question, chunks, memory):
 passages = ""
 for i, c in enumerate(chunks):
    passages += f"\n[{c['source']} p{c['page']}] {c['text']}\n"
 return f"""{SYSTEM}Conversation so far:{memory.as_text()}Passages:{passages}Current question: {question}
 Answer:"""

def answer(question, memory, k=4):
 # 1. Rewrite using history
 standalone = rewrite_query(question, memory)
 # 2. Retrieve across all docs
 chunks = search(standalone, k=k)
 # 3. Build prompt with history + sources
 prompt = build_prompt(standalone, chunks, memory)
 # 4. Generate
 resp = client.models.generate_content(
 model="gemini-2.5-flash", contents=prompt
 )
 ans = resp.text
 # 5. Save to memory (store ORIGINAL question, not rewritten)
 memory.add(question, ans)
 return {"answer": ans, "rewritten": standalone, "chunks": chunks}

if __name__ == "__main__":
 from src.govprep.generation.memory import ConversationMemory
 mem = ConversationMemory()
 for q in ["What are fundamental rights?",  
 "How many are there?", # follow-up - needs rewrite
 "Give me an example of one"]: # another follow-up
    r = answer(q, mem)
    print(f"\nQ: {q}")
    print(f"(rewritten: {r['rewritten']})")
    print(f"A: {r['answer']}")