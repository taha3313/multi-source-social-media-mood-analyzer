import asyncio
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app import main


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(main, "reddit", None)
    monkeypatch.setattr(main, "mastodon", None)
    monkeypatch.setattr(main, "YOUTUBE_API_KEY", None)
    monkeypatch.setattr(main, "embedding_model", None)
    monkeypatch.setattr(main, "emotion_classifier", None)
    return TestClient(main.app)


def test_health_and_trending_do_not_load_models(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK", "models_loaded": False, "configured_sources": []}
    assert client.get("/trending").json() == {"trending": []}
    assert main.embedding_model is None


def test_missing_credentials_are_actionable(client):
    response = client.post("/analyze", json={"topic": "climate"})
    assert response.status_code == 503
    assert "credentials" in response.json()["detail"]


@pytest.mark.parametrize("body", [
    {"topic": ""}, {"topic": "   "}, {"topic": "a" * 201},
    {"topic": "AI", "limit": -1}, {"topic": "AI", "limit": 201},
])
def test_request_bounds(client, body):
    assert client.post("/analyze", json=body).status_code == 422


def test_single_negative_score_post(monkeypatch):
    # Exercise the real inference/aggregation path with deterministic model outputs.
    import numpy as np

    post = {"text": "A sufficiently long Reddit discussion about climate policy.",
            "likes": -10, "source": "reddit", "url": "https://reddit.com/example"}

    async def fetch(_topics):
        return [post]

    monkeypatch.setattr(main, "fetch_all_sources", fetch)
    monkeypatch.setattr(main, "embedding_model", MagicMock())
    monkeypatch.setattr(main, "emotion_classifier", lambda batch: [[{"label": "anger", "score": 0.9}] for _ in batch])
    similarity = MagicMock()
    similarity.reshape.return_value.cpu.return_value.numpy.return_value = np.array([0.7])
    monkeypatch.setattr(main, "util", MagicMock(cos_sim=lambda *_: similarity))
    result = asyncio.run(main.run_analysis(main.TopicRequest(topic="climate")))
    assert result["total_posts_analyzed"] == 1
    assert result["emotion_summary"] == {"anger": 1.0}
    assert result["results"]["all_posts"][0]["similarity"] == 0.7


def test_cors_for_local_frontend(client):
    response = client.options("/analyze", headers={
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
    })
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_trending_limit_is_bounded(client):
    assert client.get("/trending?limit=10000").status_code == 422
