import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))

from ingest_v2 import ingest
from eval.score_v2 import evaluate

if __name__ == '__main__':
    print('Re-ingesting full corpus into production collection govprep_v2 with recursive 1000/100 overlap')
    ingest(force=True)
    print('\nRunning final evaluation with k=3...')
    eval_result = evaluate(k=3)
    print('\nFinal evaluation result:')
    print(eval_result)
