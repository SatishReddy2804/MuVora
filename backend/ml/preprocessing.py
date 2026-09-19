import re
import unicodedata
import json
import os
from typing import List, Dict, Tuple, Optional
import numpy as np


class TextPreprocessor:
    """
    Standard text preprocessor and sequence padder for sentiment classification.
    Adheres to the Keras IMDB dataset indexing convention:
      - 0: <PAD>
      - 1: <START>
      - 2: <UNK>
      - 3: <UNUSED>
      - 4+: word indices
    """
    PAD_INDEX = 0
    START_INDEX = 1
    UNK_INDEX = 2
    INDEX_OFFSET = 3

    def __init__(self, vocab_size: int = 10000, maxlen: int = 200):
        self.vocab_size = vocab_size
        self.maxlen = maxlen
        self.word_to_index: Dict[str, int] = {}
        self.index_to_word: Dict[int, str] = {}

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        # Unicode normalization (NFKC)
        text = unicodedata.normalize("NFKC", text)
        # Strip HTML tags
        text = re.sub(r"<[^>]+>", " ", text)
        # Lowercase
        text = text.lower()
        # Expand common contractions
        text = re.sub(r"won't", "will not", text)
        text = re.sub(r"can't", "can not", text)
        text = re.sub(r"n't", " not", text)
        text = re.sub(r"'re", " are", text)
        text = re.sub(r"'s", " is", text)
        text = re.sub(r"'d", " would", text)
        text = re.sub(r"'ll", " will", text)
        text = re.sub(r"'t", " not", text)
        text = re.sub(r"'ve", " have", text)
        text = re.sub(r"'m", " am", text)
        # Clean non-alphanumeric except basic sentence punctuation
        text = re.sub(r"[^\w\s\.\,\!\?]", " ", text)
        # Collapse multiple spaces
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def tokenize(self, text: str) -> List[str]:
        cleaned = self.clean_text(text)
        if not cleaned:
            return []
        # Match word characters (at least 1)
        tokens = re.findall(r"\b\w+\b", cleaned)
        return tokens

    def build_vocab_from_imdb(self, imdb_word_index: Dict[str, int]):
        """
        Builds vocabulary mapping from Keras IMDB word index.
        Keras IMDB word_index maps words to ranks (1 is most frequent).
        Index conventions in imdb.load_data(index_from=3):
        Word index is rank + INDEX_OFFSET.
        """
        self.word_to_index = {
            "<PAD>": self.PAD_INDEX,
            "<START>": self.START_INDEX,
            "<UNK>": self.UNK_INDEX
        }
        self.index_to_word = {
            self.PAD_INDEX: "<PAD>",
            self.START_INDEX: "<START>",
            self.UNK_INDEX: "<UNK>"
        }

        # Sort items by rank and keep up to vocab_size
        sorted_words = sorted(imdb_word_index.items(), key=lambda x: x[1])
        for word, rank in sorted_words:
            idx = rank + self.INDEX_OFFSET
            if idx < self.vocab_size:
                self.word_to_index[word] = idx
                self.index_to_word[idx] = word

    def text_to_sequence(self, text: str) -> List[int]:
        tokens = self.tokenize(text)
        # Start token
        seq = [self.START_INDEX]
        for token in tokens:
            idx = self.word_to_index.get(token, self.UNK_INDEX)
            if idx >= self.vocab_size:
                idx = self.UNK_INDEX
            seq.append(idx)
        return seq

    def pad_sequence(self, seq: List[int]) -> np.ndarray:
        """
        Pads or truncates sequence to self.maxlen.
        Pre-padding with 0 (<PAD>) to conform with standard recurrent modeling.
        """
        if len(seq) > self.maxlen:
            padded = seq[-self.maxlen:]
        else:
            padding = [self.PAD_INDEX] * (self.maxlen - len(seq))
            padded = padding + seq
        return np.array(padded, dtype=np.int32)

    def texts_to_padded_sequences(self, texts: List[str]) -> np.ndarray:
        arrays = [self.pad_sequence(self.text_to_sequence(t)) for t in texts]
        return np.stack(arrays, axis=0)

    def save_vocab(self, filepath: str):
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        data = {
            "vocab_size": self.vocab_size,
            "maxlen": self.maxlen,
            "word_to_index": self.word_to_index
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def load_vocab(self, filepath: str):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Vocabulary file not found at: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.vocab_size = data.get("vocab_size", 10000)
        self.maxlen = data.get("maxlen", 200)
        self.word_to_index = data.get("word_to_index", {})
        self.index_to_word = {int(idx): word for word, idx in self.word_to_index.items()}
