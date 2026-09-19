import time
import uuid
from typing import Optional
from backend.app.schemas.sentiment import (
    AnalyzeRequest,
    AnalyzeResponse,
    AnalysisDetail,
    KeyPhrase,
    ModelMetadata,
    CinemaNarrativeSynthesis,
    AspectSentiment
)
from backend.app.services.quality_analyzer import quality_analyzer
from backend.app.services.language_detector import language_detector
from backend.app.services.translation_service import translation_service
from backend.app.services.aspect_analyzer import aspect_analyzer
from backend.ml.predictor import predictor


class SentimentAnalysisOrchestrator:
    """
    Coordinates input quality validation, comprehensive multi-stage language/script detection,
    aspect-based sentiment evaluation, multilingual translation, neural inference,
    and localized native-script explanation.
    """

    def analyze_review(self, request: AnalyzeRequest) -> AnalyzeResponse:
        start_time = time.perf_counter()
        req_id = str(uuid.uuid4())
        raw_text = request.review.strip() if request.review else ""

        # Step 1: Comprehensive Language, Script, Transliteration, & Code-mixing Detection
        lang_detail = language_detector.detect_comprehensive(raw_text, hint=request.language_hint)
        detected_lang = lang_detail.primary_language
        lang_conf = lang_detail.confidence

        # Step 2: Quality & Random-Text Analysis
        quality_result = quality_analyzer.analyze(raw_text)
        quality_status = quality_result["quality"]
        is_usable = quality_result["is_usable"]

        # Determine display language for output
        display_lang = request.analysis_language
        if not display_lang or display_lang == "auto":
            display_lang = detected_lang

        # Step 3: Handle Low Quality / Gibberish / Out of Domain
        if not is_usable or quality_status in {"empty", "whitespace", "punctuation_only", "random_string", "out_of_domain"}:
            status_label = "out_of_domain" if quality_status == "out_of_domain" else "insufficient_input"
            summary_msg = quality_result.get("error_message") or translation_service.get_localized_summary(
                display_lang, "insufficient"
            )

            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return AnalyzeResponse(
                request_id=req_id,
                movie_title=request.movie_title,
                original_review=raw_text,
                detected_language=detected_lang,
                language_confidence=lang_conf,
                status=status_label,
                sentiment=None,
                positive_probability=0.50,
                negative_probability=0.50,
                confidence=0.0,
                review_quality=quality_status,
                translated_review=None,
                summary=summary_msg,
                analysis=AnalysisDetail(
                    overall_tone="inconclusive",
                    strength="none",
                    positive_signals=[],
                    negative_signals=[],
                    key_phrases=[]
                ),
                model=ModelMetadata(
                    name=predictor.MODEL_NAME,
                    version=predictor.MODEL_VERSION,
                    backend="tensorflow" if not predictor.is_fallback else "development_fallback"
                ),
                processing_time_ms=elapsed_ms,
                language_detection=lang_detail,
                aspects=[],
                analysis_display_language=display_lang
            )

        # Step 4: Aspect-Based Sentiment Analysis
        aspects_list = aspect_analyzer.analyze_aspects(raw_text)

        # Step 5: Multilingual Translation Flow
        # If review is non-English or transliterated, translate/normalize to English for IMDB neural classifier
        translated_text: Optional[str] = None
        text_for_inference = raw_text

        if detected_lang != "en" or lang_detail.transliterated:
            try:
                translated_text = translation_service.translate_to_english(
                    raw_text,
                    source_lang=detected_lang,
                    is_transliterated=lang_detail.transliterated
                )
                text_for_inference = translated_text
            except Exception:
                elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return AnalyzeResponse(
                    request_id=req_id,
                    movie_title=request.movie_title,
                    original_review=raw_text,
                    detected_language=detected_lang,
                    language_confidence=lang_conf,
                    status="service_error",
                    sentiment=None,
                    positive_probability=0.50,
                    negative_probability=0.50,
                    confidence=0.0,
                    review_quality=quality_status,
                    translated_review=None,
                    summary="Translation service is temporarily unavailable for this language.",
                    analysis=AnalysisDetail(
                        overall_tone="unprocessed",
                        strength="none",
                        positive_signals=[],
                        negative_signals=[],
                        key_phrases=[]
                    ),
                    model=ModelMetadata(
                        name=predictor.MODEL_NAME,
                        version=predictor.MODEL_VERSION,
                        backend="tensorflow" if not predictor.is_fallback else "development_fallback"
                    ),
                    processing_time_ms=elapsed_ms,
                    language_detection=lang_detail,
                    aspects=aspects_list,
                    analysis_display_language=display_lang
                )

        # Step 6: Neural Model Inference
        pos_prob, neg_prob, confidence = predictor.predict(text_for_inference)

        # Step 7: Result Policy & Calibration
        if pos_prob >= 0.75:
            sentiment = "positive"
            tone_key = "positive_strong" if pos_prob >= 0.88 else "positive_moderate"
        elif pos_prob <= 0.25:
            sentiment = "negative"
            tone_key = "negative_strong" if neg_prob >= 0.88 else "negative_moderate"
        else:
            sentiment = "uncertain"
            tone_key = "uncertain"

        # Step 8: Explainability & Localized Summary in requested display language
        summary = translation_service.get_localized_summary(display_lang, tone_key)
        signals = predictor.extract_key_signals(text_for_inference)

        key_phrases = [
            KeyPhrase(phrase=k["phrase"], sentiment=k["sentiment"], importance=k["importance"])
            for k in signals["key_phrases"]
        ]

        # Step 9: Meaning-Based Multi-Section Narrative Synthesis
        mentioned_aspects = [a for a in aspects_list if a.sentiment != "not_mentioned"]
        
        # Build evidence-backed aspect interpretation
        if mentioned_aspects:
            aspect_summary_lines = []
            for a in mentioned_aspects:
                quote_str = f' (evidence: "{a.evidence}")' if a.evidence else ""
                aspect_summary_lines.append(f"{a.aspect_label}: {a.sentiment.upper()}{quote_str}")
            aspect_interpretation = "; ".join(aspect_summary_lines)
        else:
            aspect_interpretation = "The review provides a holistic theatrical impression without isolating individual technical departments."

        # Tone & recommendation calculation
        if sentiment == "positive":
            reviewer_tone = f"Enthusiastic and admiring ({signals['strength']} intensity). The tone indicates genuine audience engagement."
            recommendation = "Highly Recommended for theatrical viewing." if pos_prob >= 0.85 else "Recommended for viewers who enjoy this genre."
        elif sentiment == "negative":
            reviewer_tone = f"Critical and dissatisfied ({signals['strength']} intensity). The tone expresses noticeable frustration."
            recommendation = "Skip or approach with lowered expectations." if neg_prob >= 0.85 else "Mixed appeal; viewers seeking strong storytelling may be disappointed."
        else:
            reviewer_tone = "Measured, ambivalent, or presenting balanced trade-offs."
            recommendation = "Best suited for avid fans of the actors or genre willing to overlook narrative flaws."

        # Detailed narrative
        movie_ref = f"'{request.movie_title}'" if request.movie_title else "the film"
        detailed_narrative = (
            f"The evaluation of {movie_ref} reveals a {sentiment} perspective with {round(confidence * 100)}% neural certainty. "
            f"Key expressive phrases identified in the review include {', '.join([k.phrase for k in key_phrases[:3]]) if key_phrases else 'direct opinion markers'}. "
            f"{aspect_interpretation}"
        )

        limitations = None
        if lang_detail.transliterated:
            limitations = "Review was analyzed via phonetic Romanized transliteration normalization."
        elif detected_lang != "en":
            limitations = f"Review was evaluated via multilingual translation from {lang_detail.primary_language_name}."

        synthesis_obj = CinemaNarrativeSynthesis(
            executive_summary=summary,
            detailed_narrative=detailed_narrative,
            aspect_interpretation=aspect_interpretation,
            reviewer_tone=reviewer_tone,
            recommendation=recommendation,
            limitations=limitations
        )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return AnalyzeResponse(
            request_id=req_id,
            movie_title=request.movie_title,
            original_review=raw_text,
            detected_language=detected_lang,
            language_confidence=lang_conf,
            status="success",
            sentiment=sentiment,
            positive_probability=pos_prob,
            negative_probability=neg_prob,
            confidence=confidence,
            review_quality="meaningful",
            translated_review=translated_text if (request.include_translation and (detected_lang != "en" or lang_detail.transliterated)) else None,
            summary=summary,
            analysis=AnalysisDetail(
                overall_tone=signals["overall_tone"],
                strength=signals["strength"],
                positive_signals=signals["positive_signals"],
                negative_signals=signals["negative_signals"],
                key_phrases=key_phrases,
                synthesis=synthesis_obj
            ),
            model=ModelMetadata(
                name=predictor.MODEL_NAME,
                version=predictor.MODEL_VERSION,
                backend="tensorflow" if not predictor.is_fallback else "development_fallback"
            ),
            processing_time_ms=elapsed_ms,
            language_detection=lang_detail,
            aspects=aspects_list,
            analysis_display_language=display_lang
        )


sentiment_orchestrator = SentimentAnalysisOrchestrator()
