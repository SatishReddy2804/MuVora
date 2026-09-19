from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


class TokenLanguageSpan(BaseModel):
    text: str
    language: str
    language_name: str
    script: str
    transliterated: bool = False
    confidence: float = Field(ge=0.0, le=1.0)


class LanguageAlternative(BaseModel):
    language: str
    language_name: str
    confidence: float = Field(ge=0.0, le=1.0)


class LanguageDetectionDetail(BaseModel):
    primary_language: str
    primary_language_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    script: str
    script_confidence: float = Field(ge=0.0, le=1.0)
    semantic_language: str
    transliterated: bool = False
    code_mixed: bool = False
    detection_methods: List[str] = Field(default_factory=list)
    alternatives: List[LanguageAlternative] = Field(default_factory=list)
    token_language_map: List[TokenLanguageSpan] = Field(default_factory=list)
    ambiguity_reason: Optional[str] = None


class KeyPhrase(BaseModel):
    phrase: str
    sentiment: Literal["positive", "negative", "neutral"]
    importance: float = Field(ge=0.0, le=1.0)


class AspectSentiment(BaseModel):
    aspect: str  # acting, story, direction, music, visuals, screenplay
    aspect_label: str
    sentiment: Literal["positive", "negative", "neutral", "not_mentioned"]
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: Optional[str] = None


class CinemaNarrativeSynthesis(BaseModel):
    executive_summary: str
    detailed_narrative: str
    aspect_interpretation: str
    reviewer_tone: str
    recommendation: str
    limitations: Optional[str] = None


class AnalysisDetail(BaseModel):
    overall_tone: str
    strength: str
    positive_signals: List[str] = Field(default_factory=list)
    negative_signals: List[str] = Field(default_factory=list)
    key_phrases: List[KeyPhrase] = Field(default_factory=list)
    synthesis: Optional[CinemaNarrativeSynthesis] = None


class ModelMetadata(BaseModel):
    name: str
    version: str
    backend: str


class AnalyzeRequest(BaseModel):
    movie_title: Optional[str] = Field(None, max_length=200, description="Optional title of the movie")
    review: str = Field(..., min_length=1, max_length=10000, description="The movie review or opinion text")
    language_hint: Optional[str] = Field("auto", description="ISO language code or 'auto'")
    include_translation: Optional[bool] = Field(True, description="Whether to include translated text in response")
    analysis_language: Optional[str] = Field("auto", description="Language to render analysis and explanations")
    analysis_depth: Optional[str] = Field("detailed", description="Analysis depth: 'summary' or 'detailed'")


class AnalyzeResponse(BaseModel):
    request_id: str
    movie_title: Optional[str] = None
    original_review: str
    detected_language: str
    language_confidence: float
    status: Literal["success", "insufficient_input", "out_of_domain", "unsupported_language", "service_error"]
    sentiment: Optional[Literal["positive", "negative", "uncertain"]] = None
    positive_probability: float
    negative_probability: float
    confidence: float
    review_quality: str
    translated_review: Optional[str] = None
    summary: str
    analysis: AnalysisDetail
    model: ModelMetadata
    processing_time_ms: float

    # Extended multilingual & aspect fields (optional for full backwards compatibility)
    language_detection: Optional[LanguageDetectionDetail] = None
    aspects: Optional[List[AspectSentiment]] = None
    analysis_display_language: Optional[str] = "en"


class BatchAnalyzeRequest(BaseModel):
    reviews: List[AnalyzeRequest] = Field(..., min_length=1, max_length=20)


class BatchAnalyzeResponse(BaseModel):
    results: List[AnalyzeResponse]
    total: int
    processing_time_ms: float


class DetectLanguageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    hint: Optional[str] = "auto"


class DetectLanguageResponse(BaseModel):
    input_text: str
    detection: LanguageDetectionDetail
    processing_time_ms: float


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    source_language: Optional[str] = "auto"
    target_languages: List[str] = Field(..., min_length=1, max_length=10)


class TranslateResponse(BaseModel):
    original_text: str
    detected_source: str
    detected_source_name: str
    is_transliterated: bool
    translations: Dict[str, str]
    processing_time_ms: float


class SupportedLanguageItem(BaseModel):
    code: str
    name: str
    native_name: str
    script: str
    supports_transliteration: bool = False


class SupportedLanguagesResponse(BaseModel):
    languages: List[SupportedLanguageItem]
    total: int


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str
    model_version: str


class ModelInfoResponse(BaseModel):
    name: str
    version: str
    architecture: str
    vocabulary_size: int
    max_sequence_length: int
    supported_languages: List[str]
    is_fallback: bool
    training_metrics: Optional[dict] = None


class FeedbackRequest(BaseModel):
    request_id: str
    is_helpful: bool
    comment: Optional[str] = Field(None, max_length=500)
    sentiment_rating: Optional[str] = None
