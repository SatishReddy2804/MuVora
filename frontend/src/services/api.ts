import { 
  AnalyzeRequest, 
  AnalyzeResponse, 
  ModelInfoResponse, 
  HealthResponse,
  DetectLanguageResponse,
  TranslateRequest,
  TranslateResponse,
  SupportedLanguagesResponse
} from '../types';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '') || '/api';

export async function analyzeReview(payload: AnalyzeRequest): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || `Server error: ${response.status}`);
  }

  return response.json();
}

export async function detectLanguage(text: string, hint: string = 'auto'): Promise<DetectLanguageResponse> {
  const response = await fetch(`${API_BASE}/detect-language`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, hint }),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || `Language detection failed: ${response.status}`);
  }

  return response.json();
}

export async function translateText(payload: TranslateRequest): Promise<TranslateResponse> {
  const response = await fetch(`${API_BASE}/translate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || `Translation failed: ${response.status}`);
  }

  return response.json();
}

export async function getSupportedLanguages(): Promise<SupportedLanguagesResponse> {
  const response = await fetch(`${API_BASE}/supported-languages`);
  if (!response.ok) {
    throw new Error('Failed to fetch supported languages');
  }
  return response.json();
}

export async function getModelInfo(): Promise<ModelInfoResponse> {
  const response = await fetch(`${API_BASE}/model-info`);
  if (!response.ok) {
    throw new Error('Failed to fetch model info');
  }
  return response.json();
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) {
    throw new Error('Backend health check failed');
  }
  return response.json();
}

export async function submitFeedback(requestId: string, isHelpful: boolean, comment?: string): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      request_id: requestId,
      is_helpful: isHelpful,
      comment: comment || null
    })
  });
  return response.json();
}
