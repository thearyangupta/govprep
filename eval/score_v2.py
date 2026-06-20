import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from retrieve_v2 import retrieve

def load_gold():
 with open(Path(__file__).resolve().parent / "gold_set.json") as f:
  return json.load(f)

def hit_and_rank(gold_item, k=3):
 """Returns (hit:bool, rank:int or None) for one question."""
 chunks = retrieve(gold_item["question"], k=k)
 keyword = gold_item["required_keyword"].lower()

 for rank, c in enumerate(chunks, start=1):
  if keyword in c["text"].lower():
   return True, rank
 return False, None

def evaluate(k=3):
 gold = load_gold()
 hits, reciprocal_ranks = 0, []

 for item in gold:
  hit, rank = hit_and_rank(item, k=k)

  if hit:
   hits += 1
   reciprocal_ranks.append(1.0 / rank)
  else:
   reciprocal_ranks.append(0.0)

  status = f"hit@{rank}" if hit else "MISS"
  print(f"[{status:>6}] {item['question'][:55]}")

 n = len(gold)
 hit_rate = hits / n
 mrr = sum(reciprocal_ranks) / n

 print(f"\n{'='*50}")
 print(f"Hit Rate @{k}: {hit_rate:.3f} ({hits}/{n})")
 print(f"MRR: {mrr:.3f}")

 return {"hit_rate": hit_rate, "mrr": mrr, "k": k}

if __name__ == "__main__":
 for k in [1, 3, 5, 8]:
  print(f"\n--- k = {k} ---")
  evaluate(k=k)