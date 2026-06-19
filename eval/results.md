# Eval Results
| Config                          | Hit Rate@3| MRR |
|---------------------------------|-----------|-----|
| Baseline (fixed 500 char chunks)|   0.533   |0.433|
| Recursive(500/50)               |   0.600   |0.489|


# Chunk-size sweep (recursive chunking)
|Size / Overlap	|Hit Rate@3|MRR|
|300 / 30       |0.600	 |0.489|
|500 / 50       |0.600   |0.489|
|800 / 80       |0.667	 |0.478|
|1000 / 100     |0.733	 |0.656|
Bigger chunks win on this corpus. NCERT paragraphs are long, so larger chunks keep complete ideas together. Winner: recursive 1000/100.