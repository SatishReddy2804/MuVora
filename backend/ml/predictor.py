import os
import json
import re
from typing import Tuple, Dict, Any, List
import numpy as np

from backend.app.core.logging import logger
from backend.app.core.config import settings
from backend.ml.preprocessing import TextPreprocessor


class SentimentPredictor:
    """
    Inference wrapper for the Bidirectional LSTM model.
    Loads model and vocabulary once at startup.
    Thread-safe and CPU-optimized.
    """

    MODEL_NAME = "IMDB BiLSTM Sentiment Classifier"
    MODEL_VERSION = "1.0.0"

    POSITIVE_WORDS = {
        "amazing", "excellent", "superb", "brilliant", "awesome", "fantastic", "masterpiece",
        "good", "great", "love", "loved", "enjoyed", "perfect", "flawless", "classic",
        "beautiful", "wonderful", "touching", "inspiring", "hilarious", "stunning", "best",
        "gem", "entertaining", "compelling", "impressive", "phenomenal", "captivating", "delightful"
    }

    NEGATIVE_WORDS = {
        "terrible", "horrible", "awful", "trash", "boring", "worst", "bad", "hate",
        "hated", "waste", "pathetic", "disaster", "poor", "unwatchable", "disappointing",
        "predictable", "dull", "annoying", "cliché", "ridiculous", "stupid", "mess",
        "flat", "weak", "regret", "pointless", "tedious", "crap", "garbage"
    }

    def __init__(self):
        self.model = None
        self.preprocessor = TextPreprocessor(vocab_size=settings.VOCAB_SIZE, maxlen=settings.MAX_SEQUENCE_LENGTH)
        self.is_fallback = False
        self.metadata = {}
        self.load()

    def load(self):
        """Attempts to load trained weights and vocabulary."""
        model_exists = os.path.exists(settings.MODEL_PATH)
        vocab_exists = os.path.exists(settings.VOCAB_PATH)

        if model_exists and vocab_exists:
            try:
                import tensorflow as tf
                # Optimize for CPU
                tf.config.set_visible_devices([], 'GPU')
                logger.info(f"Loading trained neural model from {settings.MODEL_PATH}...")
                self.model = tf.keras.models.load_model(settings.MODEL_PATH)
                self.preprocessor.load_vocab(settings.VOCAB_PATH)

                if os.path.exists(settings.METADATA_PATH):
                    with open(settings.METADATA_PATH, "r", encoding="utf-8") as f:
                        self.metadata = json.load(f)

                self.is_fallback = False
                logger.info("Production BiLSTM model and vocabulary successfully loaded.")
                return
            except Exception as e:
                logger.error(f"Error loading trained model: {e}. Activating development fallback.")

        logger.warning("Trained model or vocabulary not found. Activating development fallback.")
        self.is_fallback = True
        self.metadata = {
            "name": self.MODEL_NAME,
            "version": self.MODEL_VERSION,
            "backend": "development_fallback",
            "warning": "Demo fallback active — train or load the production model."
        }

    def _fallback_predict(self, cleaned_text: str) -> float:
        """
        Rule-based lexicon fallback when neural network weights have not yet been trained.
        Returns a probability between 0.05 and 0.95.
        """
        tokens = re.findall(r"\b\w+\b", cleaned_text.lower())
        if not tokens:
            return 0.50

        pos_count = sum(1 for t in tokens if t in self.POSITIVE_WORDS)
        neg_count = sum(1 for t in tokens if t in self.NEGATIVE_WORDS)

        # Check for negations before positive/negative words (e.g. "not good")
        for i in range(len(tokens) - 1):
            if tokens[i] in {"not", "never", "no", "hardly", "barely"}:
                if tokens[i+1] in self.POSITIVE_WORDS:
                    pos_count = max(0, pos_count - 1)
                    neg_count += 1
                elif tokens[i+1] in self.NEGATIVE_WORDS:
                    neg_count = max(0, neg_count - 1)
                    pos_count += 1

        total_sentiment_tokens = pos_count + neg_count
        if total_sentiment_tokens == 0:
            return 0.50

        raw_score = (pos_count - neg_count) / max(total_sentiment_tokens, 1)
        # Scale to sigmoid-like probability [0.05, 0.95]
        prob = 1.0 / (1.0 + np.exp(-raw_score * 2.5))
        return float(np.clip(prob, 0.05, 0.95))

    def predict(self, text: str) -> Tuple[float, float, float]:
        """
        Runs inference on given preprocessed text.
        Returns:
            (pos_prob, neg_prob, calibrated_confidence)
        """
        if not text or not text.strip():
            return 0.5, 0.5, 0.0

        if self.is_fallback or self.model is None:
            pos_prob = self._fallback_predict(text)
        else:
            try:
                seq = self.preprocessor.pad_sequence(self.preprocessor.text_to_sequence(text))
                batch = np.expand_dims(seq, axis=0)
                raw_pred = self.model.predict(batch, verbose=0)
                pos_prob = float(raw_pred[0][0])
            except Exception as e:
                logger.error(f"Prediction inference error: {e}. Using fallback.")
                pos_prob = self._fallback_predict(text)

        neg_prob = round(1.0 - pos_prob, 4)
        pos_prob = round(pos_prob, 4)

        # Confidence calibrated as distance from neutral 0.5 scaled to [0, 1]
        # E.g., prob=0.91 -> distance=0.41 -> 0.41*2 = 0.82 or max(pos, neg)
        # User spec states: "confidence should reflect distance from 0.5, e.g. 0.91 prob -> 0.91 or distance-based"
        # In example: positive_probability: 0.91, confidence: 0.91
        confidence = round(max(pos_prob, neg_prob), 4)

        return pos_prob, neg_prob, confidence

    def extract_key_signals(self, text: str) -> Dict[str, Any]:
        """
        Extracts salient phrases and token signals to explain prediction.
        Labeled clearly as heuristic/auxiliary analysis per guidelines.
        """
        tokens = re.findall(r"\b\w+\b", text.lower())
        pos_signals = []
        neg_signals = []
        key_phrases = []

        # Check 2-word bigrams for common patterns
        words = text.split()
        for i in range(len(words) - 1):
            w1 = words[i].lower().strip(".,!?;:\"'")
            w2 = words[i+1].lower().strip(".,!?;:\"'")
            bigram = f"{w1} {w2}"
            if w1 in {"not", "never", "hardly"} and w2 in self.POSITIVE_WORDS:
                neg_signals.append(bigram)
                key_phrases.append({"phrase": bigram, "sentiment": "negative", "importance": 0.85})
            elif w1 in {"very", "truly", "absolutely", "so", "extremely"} and w2 in self.POSITIVE_WORDS:
                pos_signals.append(bigram)
                key_phrases.append({"phrase": bigram, "sentiment": "positive", "importance": 0.90})
            elif w1 in {"very", "truly", "absolutely", "so", "extremely"} and w2 in self.NEGATIVE_WORDS:
                neg_signals.append(bigram)
                key_phrases.append({"phrase": bigram, "sentiment": "negative", "importance": 0.90})

        for t in tokens:
            if t in self.POSITIVE_WORDS and t not in [p.split()[-1] for p in pos_signals]:
                pos_signals.append(t)
                key_phrases.append({"phrase": t, "sentiment": "positive", "importance": 0.75})
            elif t in self.NEGATIVE_WORDS and t not in [p.split()[-1] for p in neg_signals]:
                neg_signals.append(t)
                key_phrases.append({"phrase": t, "sentiment": "negative", "importance": 0.75})

        # Deduplicate signals
        pos_signals = list(dict.fromkeys(pos_signals))[:5]
        neg_signals = list(dict.fromkeys(neg_signals))[:5]
        key_phrases = key_phrases[:6]

        # Tone determination
        if len(pos_signals) > len(neg_signals) * 2:
            overall_tone = "enthusiastic"
            strength = "strong"
        elif len(pos_signals) > len(neg_signals):
            overall_tone = "favorable"
            strength = "moderate"
        elif len(neg_signals) > len(pos_signals) * 2:
            overall_tone = "critical"
            strength = "strong"
        elif len(neg_signals) > len(pos_signals):
            overall_tone = "disappointed"
            strength = "moderate"
        else:
            overall_tone = "balanced / nuanced"
            strength = "mild"

        return {
            "overall_tone": overall_tone,
            "strength": strength,
            "positive_signals": pos_signals,
            "negative_signals": neg_signals,
            "key_phrases": key_phrases
        }


predictor = SentimentPredictor()
