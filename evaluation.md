# govprep - Retrieval Evaluation


## Method

- Gold set: 20 questions across NCERT polity/history/geography
- Metric: Hit Rate@3 (correct keyword in top-3) + MRR
- Proxy: keyword-in-chunk (lightweight; see limitations)
## Experiments

1. Baseline (fixed 500-char chunks)
2. Recursive chunking
3. Chunk size/overlap sweep (300-1000)
4. top-k sweep (1,3,5,8)
5. Subject metadata filtering
## Results

[paste your before/after table here]
## What I learned

- [the change that helped most]
- [a change that surprised you]
## Limitations

- Keyword proxy isn't exact relevance
- 20 questions is small; more would be more reliable
- Single embedding model tested
## Next

- Larger gold set, exact chunk-ID labels, try another embedding model
