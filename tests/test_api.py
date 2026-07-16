from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


class FakeCursor:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def execute(self, query):
        pass

    def fetchone(self):
        return (1,)


class FakeConnection:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def cursor(self):
        return FakeCursor()


class FailingConnection:
    def __enter__(self):
        raise Exception("Database unavailable")

    def __exit__(self, exc_type, exc_value, traceback):
        pass


def test_health_returns_ok(monkeypatch):
    monkeypatch.setattr(
        "app.api.get_connection",
        lambda: FakeConnection(),
    )

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": "reachable",
    }


def test_health_returns_503_when_database_fails(monkeypatch):
    monkeypatch.setattr(
        "app.api.get_connection",
        lambda: FailingConnection(),
    )

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Database is unreachable",
    }

def fake_answer(question, memory):
    return {
        "answer": "Mock Answer",
        "rewritten": "Mock Rewrite",
        "chunks": [
            {
                "source": "polity.pdf",
                "page": 10,
            }
        ],
    }


def test_chat_returns_expected_response(monkeypatch):
    monkeypatch.setattr(
        "app.api.answer",
        fake_answer,
    )

    response = client.post(
        "/chat",
        json={
            "question": "What is Article 21?"
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "answer": "Mock Answer",
        "rewritten": "Mock Rewrite",
        "sources": [
            {
                "source": "polity.pdf",
                "page": 10,
            }
        ],
    }


def test_chat_rejects_empty_question():
    response = client.post(
        "/chat",
        json={
            "question": "     "
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Question is empty",
    }