import React, { useState, useEffect } from 'react';
import { Navbar } from './components/layout/Navbar';
import { Footer } from './components/layout/Footer';
import { NeuralBackground } from './components/layout/NeuralBackground';
import { ReviewForm } from './components/analyzer/ReviewForm';
import { ResultCard } from './components/analyzer/ResultCard';
import { TranslatorWorkspace } from './components/translator/TranslatorWorkspace';
import { HistoryView } from './components/history/HistoryView';
import { InsightsView } from './components/insights/InsightsView';
import { AboutView } from './components/about/AboutView';
import { useHistory } from './hooks/useHistory';
import { analyzeReview, getHealth, getModelInfo } from './services/api';
import { AnalyzeResponse, ModelInfoResponse, HistoryItem } from './types';
import { AlertCircle } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'analyzer' | 'translator' | 'history' | 'insights' | 'about'>('analyzer');
  const [currentResult, setCurrentResult] = useState<AnalyzeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [isBackendHealthy, setIsBackendHealthy] = useState(false);
  const [modelInfo, setModelInfo] = useState<ModelInfoResponse | null>(null);

  const { history, addHistory, deleteHistoryItem, clearHistory } = useHistory();

  // Check health and model info on mount
  useEffect(() => {
    const checkSystem = async () => {
      try {
        const health = await getHealth();
        setIsBackendHealthy(health.status === 'ok');
        const info = await getModelInfo();
        setModelInfo(info);
      } catch (err) {
        setIsBackendHealthy(false);
      }
    };
    checkSystem();
    const interval = setInterval(checkSystem, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleAnalyze = async (title: string, review: string, langHint: string, analysisLang: string) => {
    setIsLoading(true);
    setApiError(null);
    try {
      const response = await analyzeReview({
        movie_title: title.trim() || undefined,
        review: review.trim(),
        language_hint: langHint,
        include_translation: true,
        analysis_language: analysisLang
      });
      setCurrentResult(response);
      addHistory(response);
    } catch (err: any) {
      setApiError(err.message || 'An error occurred while connecting to the sentiment engine.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectHistoryReview = (item: HistoryItem) => {
    setCurrentResult(item);
    setActiveTab('analyzer');
  };

  return (
    <div className="min-h-screen flex flex-col justify-between relative selection:bg-brand-violet/30 selection:text-brand-cyan">
      <NeuralBackground />
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        historyCount={history.length}
        isBackendHealthy={isBackendHealthy}
      />

      <main className="max-w-5xl w-full mx-auto px-4 sm:px-6 py-8 flex-1">
        {/* API Error Notification */}
        {apiError && (
          <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{apiError}</span>
            </div>
            <button
              onClick={() => setApiError(null)}
              className="text-slate-400 hover:text-white"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Tab Content */}
        {activeTab === 'analyzer' && (
          <div className="space-y-8">
            {/* Hero Header */}
            <div className="text-center space-y-2 max-w-2xl mx-auto">
              <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
                Understand the emotion behind every movie review.
              </h1>
              <p className="text-xs sm:text-sm text-slate-400">
                Separating physical script from semantic language, detecting transliterated Telugu & Hindi, code-mixing, and aspect-based sentiments.
              </p>
            </div>

            {/* Input Form */}
            <ReviewForm onSubmit={handleAnalyze} isLoading={isLoading} />

            {/* Results Section */}
            {currentResult && (
              <div id="results-section" className="pt-4">
                <ResultCard
                  result={currentResult}
                  onReset={() => setCurrentResult(null)}
                />
              </div>
            )}
          </div>
        )}

        {activeTab === 'translator' && (
          <TranslatorWorkspace />
        )}

        {activeTab === 'history' && (
          <HistoryView
            history={history}
            onDeleteItem={deleteHistoryItem}
            onClearHistory={clearHistory}
            onSelectReview={handleSelectHistoryReview}
          />
        )}

        {activeTab === 'insights' && (
          <InsightsView modelInfo={modelInfo} />
        )}

        {activeTab === 'about' && (
          <AboutView />
        )}
      </main>

      <Footer />
    </div>
  );
};

export default App;
