import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model_loaded" in data
    assert "model_name" in data


def test_model_info_endpoint():
    response = client.get("/api/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "architecture" in data
    assert "Embedding" in data["architecture"]
    assert "BiLSTM" in data["architecture"] or "Bidirectional" in data["architecture"]
    assert data["vocabulary_size"] == 10000


def test_analyze_positive_review():
    payload = {
        "movie_title": "Interstellar",
        "review": "I loved this movie. The acting was excellent, the story was emotional, and the ending was unforgettable."
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["sentiment"] == "positive"
    assert data["positive_probability"] >= 0.70
    assert data["confidence"] > 0.60
    assert data["review_quality"] == "meaningful"
    assert len(data["analysis"]["positive_signals"]) > 0


def test_analyze_negative_review():
    payload = {
        "movie_title": "Disaster Movie",
        "review": "This was a terrible movie with weak acting, a boring story, and a painfully predictable ending."
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["sentiment"] == "negative"
    assert data["positive_probability"] <= 0.30
    assert data["confidence"] > 0.60
    assert data["review_quality"] == "meaningful"
    assert len(data["analysis"]["negative_signals"]) > 0


def test_analyze_random_gibberish():
    payload = {
        "movie_title": "Unknown",
        "review": "hsfiiwjhfoiowfohwoehfhw"
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "insufficient_input"
    assert data["sentiment"] is None
    assert data["confidence"] == 0.0
    assert "meaningful language" in data["summary"] or "Unable to determine" in data["summary"]


def test_analyze_multilingual_hindi():
    payload = {
        "movie_title": "दंगल",
        "review": "यह फिल्म बहुत अच्छी थी और कलाकारों का अभिनय शानदार था।"
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["detected_language"] == "hi"
    assert data["status"] == "success"
    assert data["sentiment"] == "positive"
    assert data["summary"] != ""


def test_analyze_multilingual_telugu():
    payload = {
        "movie_title": "బాహుబలి",
        "review": "ఈ సినిమా చాలా బాగుంది, నటీనటుల నటన అద్భుతంగా ఉంది."
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["detected_language"] == "te"
    assert data["status"] == "success"


def test_feedback_endpoint():
    payload = {
        "request_id": "123e4567-e89b-12d3-a456-426614174000",
        "is_helpful": True,
        "comment": "Accurate prediction!"
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
