import os
from dotenv import load_dotenv
from google import genai

load_dotenv("../.env")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

REWRITE_PROMPT = """Given the conversation history and a follow-up \
question, rewrite the follow-up into a standalone question that makes \
sense without the history. Resolve all pronouns (it, they, their, that). \
If the question is already standalone, return it unchanged.
Return ONLY the rewritten question, nothing else.

Conversation history:
{history}

Follow-up question: {question}

Standalone question:"""

def rewrite_query(question, memory):
 # No history yet -> nothing to rewrite
 if not memory.turns:
  return question

 prompt = REWRITE_PROMPT.format(
  history=memory.as_text(), question=question
 )

 resp = client.models.generate_content(
  model="gemini-2.5-flash", contents=prompt
 )

 return resp.text.strip()


# Test it
if __name__ == "__main__":
 from memory import ConversationMemory

 mem = ConversationMemory()
 mem.add("Who is the President of India?",
 "The President is the head of state.")

 # Follow-up with a pronoun
 q = "what are their powers?"

 print("Original: ", q)
 print("Rewritten:", rewrite_query(q, mem))

 # Expect something like:
 # "What are the powers of the President of India?"