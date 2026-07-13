import os
import sys
from dotenv import load_dotenv

# Add scripts/ to path so we can import
sys.path.insert(0, "scripts")

from generate import answer_with_rag

def print_banner():
 print("=" * 60)
 print(" govprep_v0 - UPSC CDS Assistant")
 print(" Ask questions about loaded CDS papers")
 print(" Powered by Gemini 2.5 Flash + ChromaDB")
 print("=" * 60)
 print("Type your question, /help for commands, quit to exit.\n")

def print_help():
 print("\nCommands:")
 print(" /help - show this menu")
 print(" /sources - show chunks used in last answer")
 print(" /k <number> - change retrieval count (default: 3)")
 print(" quit - exit")
 print()

def main():
 print_banner()
 last_chunks = []
 k = 3

 while True:
  try:
   user_input = input("You: ").strip()

   if not user_input:
    continue

   if user_input.lower() == "quit":
    print("Goodbye!")
    break

   if user_input in ("/help", "/?"):
    print_help()
    continue

   if user_input == "/sources":
    if not last_chunks: #check if last_chunks is empty
     print("\nNo previous answer.\n")
    else:
     print(f"\nSources used (top {len(last_chunks)} chunks):")
     for i, chunk in enumerate(last_chunks):
      print(f"\n-- Source {i+1} (dist: {chunk['distance']:.4f}) --")
      print(chunk['text'][:300] + "...")
      print()
    continue

   if user_input.startswith("/k "): #This command changes how many chunks are retrieved.
    try:
     k = int(user_input.split()[1])
     print(f"\nNow retrieving top-{k} chunks.\n")
    except (IndexError, ValueError):
     print("\nUsage: /k <number>. Example: /k 5\n")
    continue

   # Process as a question
   #Means if input was not a command, treat it as a normal question.
   print()
   result = answer_with_rag(user_input, k=k)
   last_chunks = result['chunks_used']
   print(f"AI: {result['answer']}\n")

  except KeyboardInterrupt:
   print("\n\nInterrupted. Type 'quit' to exit cleanly.")

  except Exception as e:
   print(f"\nError: {e}\n")

if __name__ == "__main__":
 load_dotenv("../.env")

 if not os.getenv("GEMINI_API_KEY"):
  print("ERROR: GEMINI_API_KEY not found. Check .env file.")
  sys.exit(1) #1 means the program stopped because of an error.

 main()