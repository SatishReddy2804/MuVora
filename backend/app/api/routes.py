import time
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from backend.app.schemas.sentiment import (
    AnalyzeRequest,
    AnalyzeResponse,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
    DetectLanguageRequest,
    DetectLanguageResponse,
    TranslateRequest,
    TranslateResponse,
    SupportedLanguageItem,
    SupportedLanguagesResponse,
    HealthResponse,
    ModelInfoResponse,
    FeedbackRequest
)
from backend.app.services.sentiment_analyzer import sentiment_orchestrator
from backend.app.services.language_detector import language_detector
from backend.app.services.translation_service import translation_service
from backend.ml.predictor import predictor
from backend.app.core.config import settings
from backend.app.core.logging import logger

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Returns system and model health status."""
    return HealthResponse(
        status="ok",
        model_loaded=predictor.model is not None or predictor.is_fallback,
        model_name=predictor.MODEL_NAME,
        model_version=predictor.MODEL_VERSION
    )


@router.get("/model-info", response_model=ModelInfoResponse)
def model_info():
    """Returns model metadata, architecture description, and performance metrics."""
    return ModelInfoResponse(
        name=predictor.MODEL_NAME,
        version=predictor.MODEL_VERSION,
        architecture="Embedding(10000->128) -> Bidirectional(LSTM(64)) -> Dropout(0.4) -> Dense(64, ReLU) -> Dropout(0.3) -> Dense(1, Sigmoid)",
        vocabulary_size=settings.VOCAB_SIZE,
        max_sequence_length=settings.MAX_SEQUENCE_LENGTH,
        supported_languages=list(language_detector.SUPPORTED_LANGUAGES.keys()),
        is_fallback=predictor.is_fallback,
        training_metrics=predictor.metadata.get("metrics")
    )


@router.get("/supported-languages", response_model=SupportedLanguagesResponse)
def get_supported_languages():
    """Returns the registry of supported languages, scripts, and transliteration capabilities."""
    items = [
        SupportedLanguageItem(
            code=item["code"],
            name=item["name"],
            native_name=item["native_name"],
            script=item["script"],
            supports_transliteration=item.get("supports_transliteration", False)
        )
        for item in translation_service.SUPPORTED_LANGUAGES_REGISTRY
    ]
    return SupportedLanguagesResponse(languages=items, total=len(items))


@router.post("/detect-language", response_model=DetectLanguageResponse)
def detect_language(request: DetectLanguageRequest):
    """
    Performs standalone multi-stage language, script, transliteration, and code-mixing detection.
    """
    start_time = time.perf_counter()
    detail = language_detector.detect_comprehensive(request.text, hint=request.hint or "auto")
    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return DetectLanguageResponse(
        input_text=request.text,
        detection=detail,
        processing_time_ms=elapsed_ms
    )


@router.post("/translate", response_model=TranslateResponse)
def translate_text(request: TranslateRequest):
    """
    Translates input text into one or more target languages, with transliteration handling.
    """
    start_time = time.perf_counter()
    raw_text = request.text.strip()
    if not raw_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty."
        )

    # Detect language if auto
    source_lang = request.source_language or "auto"
    det_detail = language_detector.detect_comprehensive(raw_text, hint=source_lang)
    if source_lang == "auto":
        source_lang = det_detail.primary_language

    translations = translation_service.translate_multi(
        raw_text,
        source_lang=source_lang,
        target_langs=request.target_languages
    )

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    return TranslateResponse(
        original_text=raw_text,
        detected_source=source_lang,
        detected_source_name=det_detail.primary_language_name,
        is_transliterated=det_detail.transliterated,
        translations=translations,
        processing_time_ms=elapsed_ms
    )


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_review(request: AnalyzeRequest):
    """
    Analyzes an individual movie review for sentiment, quality, multilingual signals, and aspect sentiments.
    """
    try:
        response = sentiment_orchestrator.analyze_review(request)
        return response
    except Exception as e:
        logger.error(f"Unexpected error in /api/analyze: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred while processing the review."
        )


@router.post("/analyze/batch", response_model=BatchAnalyzeResponse)
def analyze_batch(request: BatchAnalyzeRequest):
    """
    Analyzes multiple movie reviews up to maximum batch size.
    """
    if len(request.reviews) > settings.MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch size exceeds limit of {settings.MAX_BATCH_SIZE} reviews."
        )

    start_time = time.perf_counter()
    results: List[AnalyzeResponse] = []
    for item in request.reviews:
        results.append(sentiment_orchestrator.analyze_review(item))

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    return BatchAnalyzeResponse(
        results=results,
        total=len(results),
        processing_time_ms=elapsed_ms
    )


@router.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    """
    Receives user feedback on sentiment analysis predictions.
    Does not log or persist private review text.
    """
    logger.info(f"Feedback received for request_id={request.request_id}: helpful={request.is_helpful}")
    return {
        "status": "success",
        "message": "Thank you for your feedback!"
    }
