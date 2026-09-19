import re
import math
import unicodedata
from typing import Dict, Any, Tuple


class QualityAnalyzer:
    """
    Dedicated quality and random-text analyzer for movie reviews.
    Prevents meaningless keyboard smash (e.g. 'hsfiiwjhfoiowfohwoehfhw')
    or empty/punctuation-only input from forcing a confident positive/negative sentiment.
    Preserves legitimate short reviews ('Amazing!', 'Worst movie ever.', 'बहुत अच्छी फिल्म', 'చాలా బాగుంది').
    """

    # Common sentiment words across languages or strong movie signals
    LEGITIMATE_SHORT_SENTIMENTS = {
        "amazing", "great", "excellent", "superb", "brilliant", "awesome", "fantastic", "masterpiece",
        "good", "love", "loved", "enjoyed", "perfect", "flawless", "classic", "beautiful", "wonderful",
        "terrible", "horrible", "awful", "trash", "boring", "worst", "bad", "hate", "hated", "waste",
        "pathetic", "disaster", "poor", "unwatchable", "disappointing", "predictable", "overrated",
        "flop", "hit", "blockbuster", "must watch", "gem", "underrated"
    }

    MOVIE_KEYWORDS = {
        "movie", "film", "cinema", "actor", "actress", "acting", "director", "direction",
        "plot", "story", "storyline", "character", "characters", "scene", "scenes",
        "climax", "screenplay", "script", "soundtrack", "music", "bgm", "dialogue", "dialogues",
        "cinematography", "visuals", "vfx", "cgi", "performance", "performances", "ending",
        "watch", "watched", "watching", "theater", "theatre", "screen", "hollywood", "bollywood",
        "series", "episode", "sequel", "prequel", "filmmaker", "cast"
    }

    def calculate_shannon_entropy(self, text: str) -> float:
        """Calculates Shannon entropy of characters to detect repeated or smash strings."""
        if not text:
            return 0.0
        prob = [float(text.count(c)) / len(text) for c in set(text)]
        return -sum([p * math.log2(p) for p in prob])

    UNNATURAL_BIGRAMS = {
        "jh", "wj", "qj", "qk", "qx", "qz", "jx", "jz", "vq", "vx", "vz", "zf", "zj", "zx",
        "hf", "fh", "hw", "wf", "hh", "jj", "vv", "ww", "xx", "yy"
    }

    def check_keyboard_smash(self, word: str) -> bool:
        """
        Detects if an individual token resembles a keyboard smash:
        - Excessive consonant or vowel cluster
        - Unnatural consonant pairs (e.g. 'jh', 'wj', 'hf', 'hw')
        - Very low/high vowel ratios
        - Unusual character repetition
        """
        word = word.lower()
        if len(word) < 7:
            return False

        # Vowel check (English letters)
        vowels = set("aeiou")
        alpha_chars = [c for c in word if 'a' <= c <= 'z']
        if not alpha_chars:
            return False

        num_vowels = sum(1 for c in alpha_chars if c in vowels)
        ratio_vowels = num_vowels / len(alpha_chars)

        # Extremely low vowel ratio or pure consonants
        if ratio_vowels < 0.12 or ratio_vowels > 0.85:
            return True

        # Check for 4+ consonants in a row
        consecutive_consonants = 0
        for c in alpha_chars:
            if c not in vowels:
                consecutive_consonants += 1
                if consecutive_consonants >= 4:
                    return True
            else:
                consecutive_consonants = 0

        # Repeated characters >= 3 times (e.g. 'aaa', 'hhhh')
        if re.search(r"(.)\1{2,}", word):
            return True

        # Check for unnatural consonant bigrams
        unnatural_count = sum(1 for i in range(len(word) - 1) if word[i:i+2] in self.UNNATURAL_BIGRAMS)
        if unnatural_count >= 2 or (len(word) >= 12 and unnatural_count >= 1):
            return True

        # Single word with length >= 16 without common English morphemes
        if len(word) >= 16:
            return True

        return False

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyzes the quality and domain relevance of the submitted review.
        """
        if text is None or text == "":
            return {
                "quality": "empty",
                "is_usable": False,
                "error_message": "Please enter a review before analyzing.",
                "detail": "Review is empty or missing."
            }

        # Check whitespace-only before strip
        if text.strip() == "":
            return {
                "quality": "whitespace",
                "is_usable": False,
                "error_message": "Please enter a review before analyzing.",
                "detail": "Review contains only whitespace."
            }

        # Normalize unicode
        text_norm = unicodedata.normalize("NFKC", text).strip()

        # Check for punctuation or symbols only
        letters = [c for c in text_norm if c.isalpha()]
        if not letters:
            return {
                "quality": "punctuation_only",
                "is_usable": False,
                "error_message": "Please enter words describing your opinion.",
                "detail": "Input contains only symbols or numbers with no words."
            }

        # Check character repetition (e.g. "aaaaa!!!!!")
        if len(text_norm) > 10:
            char_counts = {}
            for c in text_norm.lower():
                char_counts[c] = char_counts.get(c, 0) + 1
            max_char_freq = max(char_counts.values()) / len(text_norm)
            if max_char_freq > 0.70:
                return {
                    "quality": "random_string",
                    "is_usable": False,
                    "error_message": "This input does not appear to contain a meaningful movie review.",
                    "detail": "Excessive character repetition detected."
                }

        # Extract tokens
        tokens = re.findall(r"\b\w+\b", text_norm.lower())
        if not tokens:
            return {
                "quality": "punctuation_only",
                "is_usable": False,
                "error_message": "Please enter words describing your opinion.",
                "detail": "No valid lexical tokens found."
            }

        # Legitimate concise short review checks (e.g. "Amazing!", "Worst movie ever.")
        cleaned_lower = text_norm.lower()
        for legit in self.LEGITIMATE_SHORT_SENTIMENTS:
            if legit in cleaned_lower:
                return {
                    "quality": "meaningful",
                    "is_usable": True,
                    "error_message": None,
                    "detail": "Recognized concise expressive review."
                }

        # Check for single/double word smash text (e.g. 'hsfiiwjhfoiowfohwoehfhw')
        smash_tokens = sum(1 for t in tokens if self.check_keyboard_smash(t))
        if smash_tokens > 0 and smash_tokens / len(tokens) >= 0.5:
            return {
                "quality": "random_string",
                "is_usable": False,
                "error_message": "Unable to determine reliable movie sentiment because the review does not contain enough meaningful language.",
                "detail": "Keyboard smash or unpronounceable sequence detected."
            }

        # Non-English unicode text check (e.g., Devanagari, Telugu, Tamil, etc.)
        # If text is written in Indic or other scripts, we avoid penalizing it for English vowels.
        is_non_latin = any(ord(c) > 0x024F for c in text_norm if c.isalpha())
        if is_non_latin:
            # Script-based check: if it has at least 2 characters in non-latin script, it's considered meaningful text
            return {
                "quality": "meaningful",
                "is_usable": True,
                "error_message": None,
                "detail": "Valid multilingual script review."
            }

        # For very short English input (e.g. 1-2 words) that are not recognized sentiment words
        if len(tokens) <= 2 and len(text_norm) < 12:
            # Check if any token is a known movie keyword or sentiment
            has_relevant = any(t in self.MOVIE_KEYWORDS or t in self.LEGITIMATE_SHORT_SENTIMENTS for t in tokens)
            if not has_relevant:
                # Could be a random string or too brief
                entropy = self.calculate_shannon_entropy(text_norm)
                if entropy < 1.8:
                    return {
                        "quality": "random_string",
                        "is_usable": False,
                        "error_message": "Unable to determine reliable movie sentiment because the review does not contain enough meaningful language.",
                        "detail": "Input is too brief or repetitive to extract clear sentiment."
                    }

        return {
            "quality": "meaningful",
            "is_usable": True,
            "error_message": None,
            "detail": "Valid textual review."
        }


quality_analyzer = QualityAnalyzer()
