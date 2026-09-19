import unicodedata
import re
from typing import Tuple, Dict, Any, List, Optional
from backend.app.schemas.sentiment import (
    LanguageDetectionDetail,
    TokenLanguageSpan,
    LanguageAlternative
)
from backend.app.services.romanized_detector import romanized_detector

try:
    from langdetect import detect_langs, DetectorFactory
    DetectorFactory.seed = 42
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False


class LanguageDetector:
    """
    Ensemble Multilingual Language and Script Detector.
    Strictly separates:
      - Physical writing script (Unicode blocks)
      - Semantic language (Telugu, Hindi, English, etc.)
      - Transliteration / Romanization status
      - Code-mixing and token-level language identification
    """

    SUPPORTED_LANGUAGES = {
        "en": "English",
        "te": "Telugu",
        "hi": "Hindi",
        "ta": "Tamil",
        "kn": "Kannada",
        "ml": "Malayalam",
        "bn": "Bengali",
        "mr": "Marathi",
        "gu": "Gujarati",
        "pa": "Punjabi",
        "ur": "Urdu",
        "or": "Odia",
        "es": "Spanish",
        "fr": "French",
        "de": "German"
    }

    SCRIPT_MAP = {
        "Telugu": (0x0C00, 0x0C7F),
        "Devanagari": (0x0900, 0x097F),
        "Tamil": (0x0B80, 0x0BFF),
        "Kannada": (0x0C80, 0x0CFF),
        "Malayalam": (0x0D00, 0x0D7F),
        "Bengali": (0x0980, 0x09FF),
        "Gujarati": (0x0A80, 0x0AFF),
        "Gurmukhi": (0x0A00, 0x0A7F),
        "Arabic": (0x0600, 0x06FF),
        "Odia": (0x0B00, 0x0B7F)
    }

    def detect_char_script(self, char: str) -> str:
        """Determines the script category of a single character."""
        code = ord(char)
        if (0x0041 <= code <= 0x005A) or (0x0061 <= code <= 0x007A) or (0x00C0 <= code <= 0x024F):
            return "Latin"
        for script_name, (start, end) in self.SCRIPT_MAP.items():
            if start <= code <= end:
                return script_name
        return "Other"

    def analyze_scripts(self, text: str) -> Dict[str, Any]:
        """Calculates script proportions across all alphabetic characters."""
        counts = {"Latin": 0}
        for name in self.SCRIPT_MAP:
            counts[name] = 0

        total_letters = 0
        for ch in text:
            if ch.isalpha():
                total_letters += 1
                s = self.detect_char_script(ch)
                if s in counts:
                    counts[s] += 1

        if total_letters == 0:
            return {"primary_script": "Latin", "confidence": 1.0, "is_mixed_script": False, "distribution": counts}

        distribution = {k: v / total_letters for k, v in counts.items() if v > 0}
        sorted_scripts = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
        primary_script, conf = sorted_scripts[0]
        is_mixed = len(sorted_scripts) > 1 and sorted_scripts[1][1] >= 0.15

        return {
            "primary_script": primary_script,
            "confidence": round(conf, 2),
            "is_mixed_script": is_mixed,
            "distribution": distribution
        }

    def detect_comprehensive(self, text: str, hint: str = "auto") -> LanguageDetectionDetail:
        """
        Executes full multi-stage language, script, transliteration, and code-mixing analysis.
        """
        raw_text = text.strip() if text else ""
        if not raw_text:
            return LanguageDetectionDetail(
                primary_language="en",
                primary_language_name="English",
                confidence=0.5,
                script="Latin",
                script_confidence=1.0,
                semantic_language="English",
                transliterated=False,
                code_mixed=False,
                detection_methods=["default-fallback"],
                alternatives=[],
                token_language_map=[]
            )

        # Stage 1: Script Analysis
        script_info = self.analyze_scripts(raw_text)
        primary_script = script_info["primary_script"]
        script_conf = script_info["confidence"]
        is_mixed_script = script_info["is_mixed_script"]
        script_dist = script_info["distribution"]

        has_telugu_script = script_dist.get("Telugu", 0) > 0.10
        has_devanagari_script = script_dist.get("Devanagari", 0) > 0.10
        has_latin_script = script_dist.get("Latin", 0) > 0.10

        tokens = [w.strip(".,!?;:\"'()[]{}") for w in raw_text.split() if w.strip(".,!?;:\"'()[]{}")]
        token_map: List[TokenLanguageSpan] = []
        alternatives: List[LanguageAlternative] = []
        methods: List[str] = ["unicode-script-analysis"]

        # If text explicitly mixes native Indic script with Latin (e.g. "ఈ movie చాలా good ఉంది")
        if (has_telugu_script and has_latin_script) or (has_devanagari_script and has_latin_script):
            methods.append("mixed-script-detector")
            main_script = "Telugu" if has_telugu_script else "Devanagari"
            main_lang = "te" if has_telugu_script else "hi"
            main_name = "Telugu" if has_telugu_script else "Hindi"

            for t in tokens:
                first_ch_script = self.detect_char_script(t[0]) if t else "Latin"
                if first_ch_script == "Latin":
                    tok_res = romanized_detector.detect_token(t)
                    token_map.append(TokenLanguageSpan(
                        text=t,
                        language=tok_res["lang"],
                        language_name=tok_res["name"],
                        script="Latin",
                        transliterated=tok_res["transliterated"],
                        confidence=tok_res["conf"]
                    ))
                else:
                    token_map.append(TokenLanguageSpan(
                        text=t,
                        language=main_lang,
                        language_name=main_name,
                        script=main_script,
                        transliterated=False,
                        confidence=0.98
                    ))

            return LanguageDetectionDetail(
                primary_language=main_lang,
                primary_language_name=main_name,
                confidence=0.95,
                script=f"Mixed ({main_script} + Latin)",
                script_confidence=0.95,
                semantic_language=main_name,
                transliterated=False,
                code_mixed=True,
                detection_methods=methods,
                alternatives=[LanguageAlternative(language="en", language_name="English", confidence=0.20)],
                token_language_map=token_map
            )

        # Stage 2: Native Script Analysis (Telugu, Devanagari, Tamil, etc.)
        if primary_script == "Telugu":
            methods.append("native-script-detector")
            # Build token map
            for t in tokens:
                s_type = self.detect_char_script(t[0]) if t else "Telugu"
                if s_type == "Latin":
                    token_map.append(TokenLanguageSpan(
                        text=t, language="en", language_name="English", script="Latin", transliterated=False, confidence=0.90
                    ))
                else:
                    token_map.append(TokenLanguageSpan(
                        text=t, language="te", language_name="Telugu", script="Telugu", transliterated=False, confidence=0.99
                    ))

            has_latin_words = any(item.script == "Latin" for item in token_map)
            code_mixed = is_mixed_script or has_latin_words

            return LanguageDetectionDetail(
                primary_language="te",
                primary_language_name="Telugu",
                confidence=0.98,
                script="Telugu" if not is_mixed_script else "Mixed (Telugu + Latin)",
                script_confidence=script_conf,
                semantic_language="Telugu",
                transliterated=False,
                code_mixed=code_mixed,
                detection_methods=methods,
                alternatives=[LanguageAlternative(language="en", language_name="English", confidence=0.02)],
                token_language_map=token_map
            )

        elif primary_script == "Devanagari":
            methods.append("native-script-detector")
            # Distinguish Hindi vs Marathi
            is_marathi = any(w in raw_text for w in ["आहे", "होता", "झाला", "फार", "खूप", "चांगला", "नाही"])
            lang_code = "mr" if is_marathi else "hi"
            lang_name = "Marathi" if is_marathi else "Hindi"

            for t in tokens:
                s_type = self.detect_char_script(t[0]) if t else "Devanagari"
                if s_type == "Latin":
                    token_map.append(TokenLanguageSpan(
                        text=t, language="en", language_name="English", script="Latin", transliterated=False, confidence=0.90
                    ))
                else:
                    token_map.append(TokenLanguageSpan(
                        text=t, language=lang_code, language_name=lang_name, script="Devanagari", transliterated=False, confidence=0.98
                    ))

            has_latin_words = any(item.script == "Latin" for item in token_map)
            code_mixed = is_mixed_script or has_latin_words

            return LanguageDetectionDetail(
                primary_language=lang_code,
                primary_language_name=lang_name,
                confidence=0.98,
                script="Devanagari" if not is_mixed_script else "Mixed (Devanagari + Latin)",
                script_confidence=script_conf,
                semantic_language=lang_name,
                transliterated=False,
                code_mixed=code_mixed,
                detection_methods=methods,
                alternatives=[
                    LanguageAlternative(
                        language="mr" if lang_code == "hi" else "hi",
                        language_name="Marathi" if lang_code == "hi" else "Hindi",
                        confidence=0.08
                    )
                ],
                token_language_map=token_map
            )

        elif primary_script in ["Tamil", "Kannada", "Malayalam", "Bengali", "Gujarati", "Gurmukhi", "Arabic", "Odia"]:
            code_map = {
                "Tamil": ("ta", "Tamil"),
                "Kannada": ("kn", "Kannada"),
                "Malayalam": ("ml", "Malayalam"),
                "Bengali": ("bn", "Bengali"),
                "Gujarati": ("gu", "Gujarati"),
                "Gurmukhi": ("pa", "Punjabi"),
                "Arabic": ("ur", "Urdu"),
                "Odia": ("or", "Odia")
            }
            lang_code, lang_name = code_map.get(primary_script, ("en", "English"))
            methods.append("native-script-detector")

            for t in tokens:
                token_map.append(TokenLanguageSpan(
                    text=t, language=lang_code, language_name=lang_name, script=primary_script, transliterated=False, confidence=0.98
                ))

            return LanguageDetectionDetail(
                primary_language=lang_code,
                primary_language_name=lang_name,
                confidence=0.98,
                script=primary_script,
                script_confidence=script_conf,
                semantic_language=lang_name,
                transliterated=False,
                code_mixed=is_mixed_script,
                detection_methods=methods,
                alternatives=[],
                token_language_map=token_map
            )

        # Stage 3: Latin Script - Romanized Indic vs English / European Languages
        methods.append("romanized-language-classifier")
        romanized_res = romanized_detector.analyze_romanized_text(raw_text)

        primary_lang = romanized_res["primary_language"]
        transliterated = romanized_res["transliterated"]
        code_mixed = romanized_res["code_mixed"]
        conf = romanized_res["confidence"]

        # Convert token map
        for tm in romanized_res["token_map"]:
            token_map.append(TokenLanguageSpan(
                text=tm["text"],
                language=tm["language"],
                language_name=tm["language_name"],
                script="Latin",
                transliterated=tm["transliterated"],
                confidence=tm["confidence"]
            ))

        # Check manual hint override
        if hint and hint != "auto" and hint in self.SUPPORTED_LANGUAGES:
            primary_lang = hint
            conf = 1.0

        # If detected as English, run secondary langdetect for European languages (Spanish, French, German)
        if primary_lang == "en" and not transliterated and LANGDETECT_AVAILABLE:
            try:
                clean = re.sub(r"[^\w\s]", " ", raw_text).strip()
                if len(clean) >= 5:
                    probs = detect_langs(clean)
                    if probs and probs[0].lang in ["es", "fr", "de", "it", "pt"]:
                        best = probs[0]
                        primary_lang = best.lang
                        conf = round(float(best.prob), 2)
                        methods.append("ngram-statistical-model")
            except Exception:
                pass

        sem_name = self.SUPPORTED_LANGUAGES.get(primary_lang, "English")

        # Set up alternatives
        if transliterated:
            alternatives.append(LanguageAlternative(language="en", language_name="English", confidence=round(1.0 - conf, 2)))
        elif primary_lang == "en":
            alternatives.append(LanguageAlternative(language="te", language_name="Telugu", confidence=0.05))
            alternatives.append(LanguageAlternative(language="hi", language_name="Hindi", confidence=0.05))

        return LanguageDetectionDetail(
            primary_language=primary_lang,
            primary_language_name=sem_name,
            confidence=conf,
            script="Latin",
            script_confidence=script_conf,
            semantic_language=sem_name,
            transliterated=transliterated,
            code_mixed=code_mixed,
            detection_methods=methods,
            alternatives=alternatives,
            token_language_map=token_map,
            ambiguity_reason="Low-confidence detection" if conf < 0.65 else None
        )

    def detect(self, text: str, hint: str = "auto") -> Tuple[str, float]:
        """
        Legacy signature preserved for 100% backward compatibility.
        Returns: (lang_code, confidence)
        """
        detail = self.detect_comprehensive(text, hint=hint)
        return detail.primary_language, detail.confidence


language_detector = LanguageDetector()
