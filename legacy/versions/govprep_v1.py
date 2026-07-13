import os, sys
from dotenv import load_dotenv

sys.path.insert(0, "scripts")

from memory import ConversationMemory
from generate_v1 import answer

def banner():
 print("=" * 58)
 print(" govprep_v1 - UPSC/CDS Assistant (multi-doc + memory)")
 print(" Sources: NCERT Polity, History, Geography")
 print("=" * 58)
 print("Commands: /sources, /reset, /history, quit\n")

def main():
 banner()

 mem = ConversationMemory()
 last = None

 while True:
  try:
   q = input("You: ").strip()

   if not q:
    continue

   if q.lower() == "quit":
    print("Bye!"); break

   if q == "/reset":
    mem = ConversationMemory(); print("Memory cleared.\n"); continue

   if q == "/history":
    print(mem.as_text(), "\n"); continue

   if q == "/sources":
    if last:
     for c in last["chunks"]:
      print(f" [{c['source']} p{c['page']}] {c['text'][:90]}...")
     print(); continue

   last = answer(q, mem)

   print(f"\nAI: {last['answer']}\n")

  except Exception as e:
   print(f"Error: {e}\n")

if __name__ == "__main__":
 load_dotenv(".env")

 if not os.getenv("GEMINI_API_KEY"):
  print("ERROR: GEMINI_API_KEY missing"); sys.exit(1)

 main()