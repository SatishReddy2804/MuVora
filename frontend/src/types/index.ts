export type SentimentType = 'positive' | 'negative' | 'uncertain' | null;

export type AnalysisStatus = 
  | 'success'
  | 'insufficient_input'
  | 'out_of_domain'
  | 'unsupported_language'
  | 'service_error';

export interface KeyPhrase {
  phrase: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  importance: number;
}

export interface AspectSentiment {
  aspect: string;
  aspect_label: string;
  sentiment: 'positive' | 'negative' | 'neutral' | 'not_mentioned';
  confidence: number;
  evidence?: string | null;
}

export interface TokenLanguageSpan {
  text: string;
  language: string;
  language_name: string;
  script: string;
  transliterated: boolean;
  confidence: number;
}

export interface LanguageAlternative {
  language: string;
  language_name: string;
  confidence: number;
}

export interface LanguageDetectionDetail {
  primary_language: string;
  primary_language_name: string;
  confidence: number;
  script: string;
  script_confidence: number;
  semantic_language: string;
  transliterated: boolean;
  code_mixed: boolean;
  detection_methods: string[];
  alternatives: LanguageAlternative[];
  token_language_map: TokenLanguageSpan[];
  ambiguity_reason?: string | null;
}

export interface CinemaNarrativeSynthesis {
  executive_summary: string;
  detailed_narrative: string;
  aspect_interpretation: string;
  reviewer_tone: string;
  recommendation: string;
  limitations?: string | null;
}

export interface AnalysisDetail {
  overall_tone: string;
  strength: string;
  positive_signals: string[];
  negative_signals: string[];
  key_phrases: KeyPhrase[];
  synthesis?: CinemaNarrativeSynthesis | null;
}

export interface ModelMetadata {
  name: string;
  version: string;
  backend: string;
}

export interface AnalyzeResponse {
  request_id: string;
  movie_title?: string | null;
  original_review: string;
  detected_language: string;
  language_confidence: number;
  status: AnalysisStatus;
  sentiment: SentimentType;
  positive_probability: number;
  negative_probability: number;
  confidence: number;
  review_quality: string;
  translated_review?: string | null;
  summary: string;
  analysis: AnalysisDetail;
  model: ModelMetadata;
  processing_time_ms: number;

  // Extended multilingual & aspect fields
  language_detection?: LanguageDetectionDetail | null;
  aspects?: AspectSentiment[] | null;
  analysis_display_language?: string | null;
}

export interface AnalyzeRequest {
  movie_title?: string;
  review: string;
  language_hint?: string;
  include_translation?: boolean;
  analysis_language?: string;
  analysis_depth?: string;
}

export interface DetectLanguageRequest {
  text: string;
  hint?: string;
}

export interface DetectLanguageResponse {
  input_text: string;
  detection: LanguageDetectionDetail;
  processing_time_ms: number;
}

export interface TranslateRequest {
  text: string;
  source_language?: string;
  target_languages: string[];
}

export interface TranslateResponse {
  original_text: string;
  detected_source: string;
  detected_source_name: string;
  is_transliterated: boolean;
  translations: Record<string, string>;
  processing_time_ms: number;
}

export interface SupportedLanguageItem {
  code: string;
  name: string;
  native_name: string;
  script: string;
  supports_transliteration: boolean;
}

export interface SupportedLanguagesResponse {
  languages: SupportedLanguageItem[];
  total: number;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  model_name: string;
  model_version: string;
}

export interface ModelInfoResponse {
  name: string;
  version: string;
  architecture: string;
  vocabulary_size: number;
  max_sequence_length: number;
  supported_languages: string[];
  is_fallback: boolean;
  training_metrics?: {
    accuracy: number;
    precision: number;
    recall: number;
    f1: number;
    roc_auc: number;
    confusion_matrix: {
      true_negative: number;
      false_positive: number;
      false_negative: number;
      true_positive: number;
      matrix: number[][];
    };
    threshold: number;
  } | null;
}

export interface HistoryItem extends AnalyzeResponse {
  saved_at: string;
}
