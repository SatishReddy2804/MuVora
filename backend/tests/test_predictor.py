import pytest
from backend.ml.preprocessing import TextPreprocessor
from backend.ml.predictor import predictor
from backend.ml.metrics import compute_classification_metrics


def test_preprocessor_clean_and_tokenize():
    prep = TextPreprocessor(vocab_size=1000, maxlen=20)
    cleaned = prep.clean_text("<p>Don't watch this terrible movie!</p>")
    assert "do not watch this terrible movie" in cleaned
    tokens = prep.tokenize(cleaned)
    assert "terrible" in tokens
    assert "movie" in tokens


def test_preprocessor_padding():
    prep = TextPreprocessor(vocab_size=1000, maxlen=10)
    prep.word_to_index = {"<PAD>": 0, "<START>": 1, "<UNK>": 2, "great": 4, "movie": 5}
    seq = prep.text_to_sequence("great movie")
    padded = prep.pad_sequence(seq)
    assert len(padded) == 10
    # First tokens should be 0 (<PAD>)
    assert padded[0] == 0
    # Last tokens should end with movie
    assert padded[-1] == 5


def test_metrics_calculation():
    y_true = [1, 0, 1, 1, 0, 0]
    y_probs = [0.9, 0.1, 0.8, 0.4, 0.2, 0.3]
    metrics = compute_classification_metrics(y_true, y_probs, threshold=0.5)
    assert "accuracy" in metrics
    assert "confusion_matrix" in metrics
    assert metrics["accuracy"] >= 0.80
