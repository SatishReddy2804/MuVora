import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.language_detector import language_detector
from backend.app.services.aspect_analyzer import aspect_analyzer

client = TestClient(app)


def test_native_telugu_script_detection():
    text = "సినిమా చాలా బాగుంది"
    res = language_detector.detect_comprehensive(text)
    assert res.primary_language == "te"
    assert res.script == "Telugu"
    assert res.semantic_language == "Telugu"
    assert res.transliterated is False


def test_romanized_telugu_detection():
    text = "cinema chala bagundhi"
    res = language_detector.detect_comprehensive(text)
    assert res.primary_language == "te"
    assert res.script == "Latin"
    assert res.semantic_language == "Telugu"
    assert res.transliterated is True


def test_native_hindi_script_detection():
    text = "फिल्म बहुत अच्छी है"
    res = language_detector.detect_comprehensive(text)
    assert res.primary_language == "hi"
    assert res.script == "Devanagari"
    assert res.semantic_language == "Hindi"
    assert res.transliterated is False


def test_romanized_hindi_detection():
    text = "movie bahut accha hai"
    res = language_detector.detect_comprehensive(text)
    assert res.primary_language == "hi"
    assert res.script == "Latin"
    assert res.semantic_language == "Hindi"
    assert res.transliterated is True


def test_code_mixed_telugu_english():
    text = "Movie chala bagundhi"
    res = language_detector.detect_comprehensive(text)
    assert res.primary_language == "te"
    assert res.code_mixed is True
    tokens = [t.text.lower() for t in res.token_language_map]
    assert "movie" in tokens
    assert "chala" in tokens


def test_mixed_script_telugu_english():
    text = "ఈ movie చాలా good ఉంది"
    res = language_detector.detect_comprehensive(text)
    assert res.code_mixed is True
    assert "Telugu" in res.script


def test_code_mixed_hindi_english():
    text = "Movie bahut acchi hai, acting super"
    res = language_detector.detect_comprehensive(text)
    assert res.primary_language == "hi"
    assert res.code_mixed is True


def test_api_detect_language_endpoint():
    payload = {"text": "cinema chala bagundhi"}
    response = client.post("/api/detect-language", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["detection"]["primary_language"] == "te"
    assert data["detection"]["script"] == "Latin"
    assert data["detection"]["transliterated"] is True


def test_api_translate_endpoint():
    payload = {
        "text": "The movie is very good.",
        "source_language": "en",
        "target_languages": ["te", "hi"]
    }
    response = client.post("/api/translate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "te" in data["translations"]
    assert "hi" in data["translations"]


def test_api_supported_languages_endpoint():
    response = client.get("/api/supported-languages")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 15
    codes = [l["code"] for l in data["languages"]]
    assert "en" in codes and "te" in codes and "hi" in codes


def test_aspect_analyzer_evidence():
    review = "The acting was excellent and breathtaking. However, the story was terribly boring and predictable."
    aspects = aspect_analyzer.analyze_aspects(review)
    aspect_map = {a.aspect: a for a in aspects}

    assert aspect_map["acting"].sentiment == "positive"
    assert "acting was excellent" in aspect_map["acting"].evidence.lower()

    assert aspect_map["story"].sentiment == "negative"
    assert "story was terribly boring" in aspect_map["story"].evidence.lower()

    # Direction was not mentioned
    assert aspect_map["direction"].sentiment == "not_mentioned"
    assert aspect_map["direction"].evidence is None
