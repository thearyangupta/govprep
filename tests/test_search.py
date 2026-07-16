from govprep.retrieval.search import search


def test_search_calls_hybrid_search(monkeypatch):
    captured = {}

    fake_results = [
        {
            "text": "Article 21 protects life and personal liberty.",
            "source": "Polity",
            "page": 87,
            "rrf_score": 0.42,
        }
    ]

    def fake_hybrid_search(query, k):
        captured["query"] = query
        captured["k"] = k
        return fake_results

    monkeypatch.setattr(
        "govprep.retrieval.search.hybrid_search",
        fake_hybrid_search,
    )

    result = search("Article 21", k=4)

    assert captured["query"] == "Article 21"
    assert captured["k"] == 4
    assert result == fake_results