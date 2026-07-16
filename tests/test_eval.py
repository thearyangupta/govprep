from eval.pg_score import evaluate_question


def test_evaluate_question_smoke(monkeypatch):
    fake_chunks = [
        {
            "text": (
                "Article 21 protects life and personal liberty "
                "under the Constitution of India."
            ),
            "source": "Polity",
            "page": 87,
        }
    ]

    def fake_get_chunks(question, mode, k):
        return fake_chunks

    monkeypatch.setattr(
        "eval.pg_score.get_chunks",
        fake_get_chunks,
    )

    gold_item = {
        "question": "What does Article 21 protect?",
        "required_keyword": "personal liberty",
    }

    result = evaluate_question(
        gold_item=gold_item,
        mode="hybrid",
        k=3,
    )

    assert result["question"] == (
        "What does Article 21 protect?"
    )
    assert result["required_keyword"] == "personal liberty"
    assert result["hit"] is True
    assert result["rank"] == 1
    assert result["reciprocal_rank"] == 1.0
    assert result["retrieved_chunks"] == fake_chunks