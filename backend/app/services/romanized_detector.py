import re
from typing import Dict, List, Tuple, Optional, Any


class RomanizedDetector:
    """
    Identifies Romanized/Transliterated Indian languages written in Latin script
    (Telugu, Hindi, Tamil, Kannada, Malayalam, etc.) and analyzes token-level code mixing.
    """

    TELUGU_WORDS = {
        "chala", "chaala", "bagundi", "bagundhi", "baagundhi", "bavundi", "baavundi",
        "nachindi", "nachindhi", "nachaledu", "nachala", "nachinatlu",
        "undhi", "undi", "vundhi", "vundi", "unayi", "unnayi", "untaadi",
        "chesaru", "chepparu", "chusesa", "chusa", "choosa", "chusanu", "choosanu",
        "choodandi", "chudandi", "anipinchindi", "anipisthondi",
        "koddiga", "konchem", "chala bagundi", "super undhi", "adbhutam",
        "pedda", "chinna", "manchi", "goppa", "daridram", "rod", "bokka", "waste",
        "cinema", "cinemalo", "cinemaaki", "chithram", "patalu", "paatalu", "songlu",
        "fightlu", "climax", "kaani", "kani", "kuda", "kooda", "ani", "mari",
        "eppudu", "ippudu", "ela", "yela", "em", "enti", "enduku", "naaku", "naku",
        "meeru", "nenu", "vaallu", "heroine", "villain", "acting", "director", "bale",
        "keka", "thop", "arachakam", "iraga", "dhimma"
    }

    HINDI_WORDS = {
        "bahut", "bohot", "bahuth", "bhot", "accha", "acha", "achha", "achi", "acchi",
        "bura", "kharab", "bekaar", "bekar", "bakwas", "bakwaas", "kahaani", "kahani",
        "pasand", "aaya", "aayi", "aaye", "hai", "hain", "tha", "thi", "the",
        "mujhe", "muze", "hamein", "hume", "mera", "meri", "mere", "apna", "apni",
        "dekh", "dekha", "dekhi", "dekhne", "dekhna", "film", "filam", "gaane", "gana",
        "mast", "jabardast", "zabardast", "shandar", "shaandaar", "laajawab", "badiya",
        "badhiya", "kamaal", "dhamaal", "ekdam", "bilkul", "thoda", "thodi", "zyada",
        "jyada", "lekin", "magar", "par", "kuch", "kya", "kyu", "kyun", "kaise",
        "acting", "dialogue", "storyline", "climax", "bore", "paisa vasool", "samajh",
        "laga", "lagi", "lage", "nahin", "nahi", "mat", "karo", "kiya"
    }

    TAMIL_WORDS = {
        "romba", "nalla", "irukku", "padam", "semma", "super", "nadipu", "paatu",
        "kevalam", "mokkai", "oru", "indha", "andha", "kadhai", "thalaiva", "marana"
    }

    KANNADA_WORDS = {
        "tumba", "chennagide", "channagide", "chithra", "nodi", "chennagi", "ishta",
        "ondhu", "kathe", "nanna", "hegidhe"
    }

    MALAYALAM_WORDS = {
        "valare", "nannayittundu", "nalla", "cinemayil", "adipoli", "kollam", "polichu",
        "padam", "abhinayam", "chithram"
    }

    COMMON_ENGLISH_WORDS = {
        "the", "a", "an", "is", "was", "are", "were", "this", "that", "it", "movie",
        "film", "acting", "actor", "story", "director", "direction", "and", "or",
        "but", "with", "very", "good", "bad", "great", "worst", "best", "loved",
        "liked", "watching", "watched", "cinema", "screenplay", "music", "songs",
        "ending", "climax", "plot", "cast", "performance", "performances", "ever",
        "superb", "brilliant", "terrible", "boring", "waste", "time", "masterpiece"
    }

    def detect_token(self, token: str) -> Dict[str, Any]:
        """Classifies an individual alphanumeric Latin token."""
        tok = token.lower()

        # Check Telugu
        if tok in self.TELUGU_WORDS:
            return {"lang": "te", "name": "Telugu", "transliterated": True, "conf": 0.95}
        if tok.endswith("ndhi") or tok.endswith("indi") or tok.endswith("aaru") or tok.endswith("aadu"):
            return {"lang": "te", "name": "Telugu", "transliterated": True, "conf": 0.85}

        # Check Hindi
        if tok in self.HINDI_WORDS:
            return {"lang": "hi", "name": "Hindi", "transliterated": True, "conf": 0.95}
        if tok.endswith("wala") or tok.endswith("wali") or tok.endswith("pana"):
            return {"lang": "hi", "name": "Hindi", "transliterated": True, "conf": 0.85}

        # Check Tamil, Kannada, Malayalam
        if tok in self.TAMIL_WORDS:
            return {"lang": "ta", "name": "Tamil", "transliterated": True, "conf": 0.95}
        if tok in self.KANNADA_WORDS:
            return {"lang": "kn", "name": "Kannada", "transliterated": True, "conf": 0.95}
        if tok in self.MALAYALAM_WORDS:
            return {"lang": "ml", "name": "Malayalam", "transliterated": True, "conf": 0.95}

        # Check English
        if tok in self.COMMON_ENGLISH_WORDS:
            return {"lang": "en", "name": "English", "transliterated": False, "conf": 0.90}

        return {"lang": "en", "name": "English", "transliterated": False, "conf": 0.50}

    def analyze_romanized_text(self, text: str) -> Dict[str, Any]:
        """
        Analyzes Latin-script text to determine whether it is Romanized Indian language,
        English, or Code-mixed.
        """
        raw_tokens = re.findall(r"\b\w+\b", text)
        if not raw_tokens:
            return {
                "primary_language": "en",
                "primary_language_name": "English",
                "confidence": 0.5,
                "transliterated": False,
                "code_mixed": False,
                "token_map": []
            }

        counts = {"te": 0, "hi": 0, "ta": 0, "kn": 0, "ml": 0, "en": 0}
        token_map = []

        for raw_tok in raw_tokens:
            t_res = self.detect_token(raw_tok)
            lang = t_res["lang"]
            counts[lang] += 1
            token_map.append({
                "text": raw_tok,
                "language": lang,
                "language_name": t_res["name"],
                "script": "Latin",
                "transliterated": t_res["transliterated"],
                "confidence": t_res["conf"]
            })

        total = len(raw_tokens)
        te_ratio = counts["te"] / total
        hi_ratio = counts["hi"] / total
        ta_ratio = counts["ta"] / total
        kn_ratio = counts["kn"] / total
        ml_ratio = counts["ml"] / total
        en_ratio = counts["en"] / total

        # Check for phrase patterns like "chala bagundhi", "bahut accha hai", etc.
        text_lower = text.lower()
        has_te_phrase = any(p in text_lower for p in ["chala bagund", "bagundhi", "bagundi", "chala nach", "nachindi", "acting super undhi", "rod cinema"])
        has_hi_phrase = any(p in text_lower for p in ["bahut acch", "bahut ach", "bohot ach", "pasand aay", "kahaani ach", "acting super hai"])

        if has_te_phrase:
            te_ratio += 0.35
        if has_hi_phrase:
            hi_ratio += 0.35

        # Decision
        primary_lang = "en"
        transliterated = False
        conf = 0.90

        if te_ratio >= 0.25 or has_te_phrase:
            primary_lang = "te"
            transliterated = True
            conf = min(0.98, 0.75 + te_ratio * 0.25)
        elif hi_ratio >= 0.25 or has_hi_phrase:
            primary_lang = "hi"
            transliterated = True
            conf = min(0.98, 0.75 + hi_ratio * 0.25)
        elif ta_ratio >= 0.25:
            primary_lang = "ta"
            transliterated = True
            conf = 0.85
        elif kn_ratio >= 0.25:
            primary_lang = "kn"
            transliterated = True
            conf = 0.85
        elif ml_ratio >= 0.25:
            primary_lang = "ml"
            transliterated = True
            conf = 0.85
        else:
            primary_lang = "en"
            transliterated = False
            conf = 0.92

        # Code-mixed determination: having tokens from multiple languages (e.g. English words + Telugu words)
        active_langs = [k for k, v in counts.items() if v > 0]
        code_mixed = False
        if len(active_langs) > 1 and (te_ratio > 0.15 or hi_ratio > 0.15 or ta_ratio > 0.15) and en_ratio > 0.15:
            code_mixed = True

        name_map = {
            "en": "English",
            "te": "Telugu",
            "hi": "Hindi",
            "ta": "Tamil",
            "kn": "Kannada",
            "ml": "Malayalam"
        }

        return {
            "primary_language": primary_lang,
            "primary_language_name": name_map.get(primary_lang, "English"),
            "confidence": round(conf, 2),
            "transliterated": transliterated,
            "code_mixed": code_mixed,
            "token_map": token_map
        }


romanized_detector = RomanizedDetector()
