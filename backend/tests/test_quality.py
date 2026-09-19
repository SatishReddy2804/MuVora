import pytest
from backend.app.services.quality_analyzer import quality_analyzer


def test_empty_review():
    res = quality_analyzer.analyze("")
    assert res["is_usable"] is False
    assert res["quality"] == "empty"


def test_whitespace_review():
    res = quality_analyzer.analyze("    \n\t  ")
    assert res["is_usable"] is False
    assert res["quality"] == "whitespace"


def test_punctuation_only():
    res = quality_analyzer.analyze("...???!!! ---")
    assert res["is_usable"] is False
    assert res["quality"] == "punctuation_only"


def test_keyboard_smash_random_string():
    res = quality_analyzer.analyze("hsfiiwjhfoiowfohwoehfhw")
    assert res["is_usable"] is False
    assert res["quality"] == "random_string"


def test_character_repetition():
    res = quality_analyzer.analyze("aaaaaaaabbbbbbbb")
    assert res["is_usable"] is False
    assert res["quality"] == "random_string"


def test_legitimate_short_positive():
    res = quality_analyzer.analyze("Amazing!")
    assert res["is_usable"] is True
    assert res["quality"] == "meaningful"


def test_legitimate_short_negative():
    res = quality_analyzer.analyze("Worst movie ever.")
    assert res["is_usable"] is True
    assert res["quality"] == "meaningful"


def test_multilingual_hindi_short():
    res = quality_analyzer.analyze("बहुत अच्छी फिल्म")
    assert res["is_usable"] is True
    assert res["quality"] == "meaningful"


def test_multilingual_telugu_short():
    res = quality_analyzer.analyze("చాలా బాగుంది")
    assert res["is_usable"] is True
    assert res["quality"] == "meaningful"
