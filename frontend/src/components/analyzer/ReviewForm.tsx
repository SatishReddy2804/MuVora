import React, { useState } from 'react';
import { Send, RotateCcw, Sparkles, Globe, Film, HelpCircle, Languages } from 'lucide-react';
import { GlassCard } from '../ui/GlassCard';

interface ReviewFormProps {
  onSubmit: (title: string, review: string, langHint: string, analysisLang: string) => void;
  isLoading: boolean;
}

export const ReviewForm: React.FC<ReviewFormProps> = ({ onSubmit, isLoading }) => {
  const [movieTitle, setMovieTitle] = useState('');
  const [review, setReview] = useState('');
  const [languageHint, setLanguageHint] = useState('auto');
  const [analysisLang, setAnalysisLang] = useState('auto');
  const [error, setError] = useState<string | null>(null);

  const sampleReviews = [
    {
      label: 'Positive Sample',
      title: 'Interstellar (2014)',
      text: 'I loved this movie. The acting was excellent, the story was emotional, and the ending was unforgettable.',
      lang: 'en'
    },
    {
      label: 'Negative Sample',
      title: 'The Room (2003)',
      text: 'This was a terrible movie with weak acting, a boring story, and a painfully predictable ending.',
      lang: 'en'
    },
    {
      label: 'Romanized Telugu',
      title: 'RRR (2022)',
      text: 'cinema chala bagundhi, acting super undhi and visual effects adbhutam.',
      lang: 'auto'
    },
    {
      label: 'Romanized Hindi',
      title: 'Jawan (2023)',
      text: 'movie bahut accha hai, acting zabardast hai aur gaane mast hain.',
      lang: 'auto'
    },
    {
      label: 'Code-Mixed Te-En',
      title: 'Kalki 2898 AD',
      text: 'Movie chala bagundhi, direction was great and story is good.',
      lang: 'auto'
    },
    {
      label: 'Native Telugu',
      title: 'బాహుబలి',
      text: 'ఈ సినిమా చాలా బాగుంది, నటీనటుల నటన అద్భుతంగా ఉంది.',
      lang: 'te'
    },
    {
      label: 'Native Hindi',
      title: 'दंगल',
      text: 'यह फिल्म बहुत अच्छी थी और कलाकारों का अभिनय शानदार था।',
      lang: 'hi'
    },
    {
      label: 'Keyboard Smash',
      title: '',
      text: 'hsfiiwjhfoiowfohwoehfhw',
      lang: 'auto'
    }
  ];

  const handleApplySample = (sample: typeof sampleReviews[0]) => {
    setMovieTitle(sample.title);
    setReview(sample.text);
    setLanguageHint(sample.lang);
    setError(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!review.trim()) {
      setError('Please enter a review before analyzing.');
      return;
    }
    setError(null);
    onSubmit(movieTitle, review, languageHint, analysisLang);
  };

  const handleClear = () => {
    setMovieTitle('');
    setReview('');
    setError(null);
  };

  return (
    <GlassCard className="w-full relative overflow-hidden">
      <div className="absolute -top-24 -right-24 w-48 h-48 bg-brand-violet/20 rounded-full blur-3xl pointer-events-none" />

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Row 1: Movie Title & Language Selectors */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
          <div className="sm:col-span-2 space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
              <Film className="w-3.5 h-3.5 text-brand-cyan" />
              Movie Title <span className="text-slate-500 font-normal">(Optional)</span>
            </label>
            <input
              type="text"
              value={movieTitle}
              onChange={(e) => setMovieTitle(e.target.value)}
              placeholder="e.g. Oppenheimer, RRR, Baahubali..."
              maxLength={200}
              disabled={isLoading}
              className="w-full px-3.5 py-2 rounded-xl bg-surface-light/70 border border-white/10 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-cyan transition-all"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
              <Globe className="w-3.5 h-3.5 text-brand-violet" />
              Input Language
            </label>
            <select
              value={languageHint}
              onChange={(e) => setLanguageHint(e.target.value)}
              disabled={isLoading}
              className="w-full px-3 py-2 rounded-xl bg-surface-light/70 border border-white/10 text-xs text-white focus:outline-none focus:border-brand-violet transition-all"
            >
              <option value="auto">🌐 Auto Detect</option>
              <option value="en">English</option>
              <option value="te">తెలుగు (Telugu)</option>
              <option value="hi">हिन्दी (Hindi)</option>
              <option value="ta">தமிழ் (Tamil)</option>
              <option value="kn">ಕನ್ನಡ (Kannada)</option>
              <option value="ml">മലയാളം (Malayalam)</option>
              <option value="bn">বাংলা (Bengali)</option>
              <option value="mr">मराठी (Marathi)</option>
              <option value="es">Español (Spanish)</option>
              <option value="fr">Français (French)</option>
              <option value="de">Deutsch (German)</option>
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
              <Languages className="w-3.5 h-3.5 text-brand-cyan" />
              Display Language
            </label>
            <select
              value={analysisLang}
              onChange={(e) => setAnalysisLang(e.target.value)}
              disabled={isLoading}
              className="w-full px-3 py-2 rounded-xl bg-surface-light/70 border border-white/10 text-xs text-white focus:outline-none focus:border-brand-cyan transition-all"
            >
              <option value="auto">🌐 Match Review</option>
              <option value="en">English (Default)</option>
              <option value="te">తెలుగు (Telugu Script)</option>
              <option value="hi">हिन्दी (Devanagari)</option>
              <option value="ta">தமிழ் (Tamil)</option>
              <option value="kn">ಕನ್ನಡ (Kannada)</option>
              <option value="es">Español</option>
              <option value="fr">Français</option>
            </select>
          </div>
        </div>

        {/* Row 2: Review Textarea */}
        <div className="space-y-1.5">
          <div className="flex justify-between items-center">
            <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-brand-cyan" />
              Movie Review / Audience Opinion <span className="text-rose-400">*</span>
            </label>
            <span className={`text-[11px] font-mono ${review.length > 9000 ? 'text-amber-400' : 'text-slate-500'}`}>
              {review.length} / 10,000
            </span>
          </div>

          <textarea
            value={review}
            onChange={(e) => {
              setReview(e.target.value);
              if (error) setError(null);
            }}
            placeholder="Write your review in English, Telugu, Hindi, or Romanized transliterations (e.g. 'cinema chala bagundhi', 'movie bahut accha hai')..."
            rows={5}
            maxLength={10000}
            disabled={isLoading}
            className="w-full px-4 py-3 rounded-xl bg-surface-light/70 border border-white/10 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-cyan transition-all resize-y"
          />

          {error && (
            <p className="text-xs text-rose-400 mt-1 flex items-center gap-1">
              {error}
            </p>
          )}
        </div>

        {/* Row 3: Sample Reviews buttons */}
        <div className="space-y-1.5 pt-1">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
            Try Sample Reviews (Including Transliterated & Code-Mixed):
          </span>
          <div className="flex flex-wrap gap-2">
            {sampleReviews.map((sample, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleApplySample(sample)}
                disabled={isLoading}
                className="px-2.5 py-1 rounded-lg text-xs font-medium bg-white/[0.04] hover:bg-white/[0.08] text-slate-300 border border-white/[0.06] transition-all hover:scale-[1.02]"
              >
                {sample.label}
              </button>
            ))}
          </div>
        </div>

        {/* Row 4: Actions */}
        <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-white/[0.06]">
          <button
            type="button"
            onClick={handleClear}
            disabled={isLoading || (!movieTitle && !review)}
            className="w-full sm:w-auto px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-400 hover:text-white bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.06] flex items-center justify-center gap-1.5 transition-all disabled:opacity-40"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Clear Form
          </button>

          <button
            type="submit"
            disabled={isLoading || !review.trim()}
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider text-white bg-gradient-to-r from-brand-violet via-indigo-600 to-brand-cyan hover:opacity-95 shadow-lg shadow-brand-violet/20 flex items-center justify-center gap-2 transition-all hover:scale-[1.02] disabled:opacity-50 disabled:hover:scale-100"
          >
            {isLoading ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Analyzing Multilingual Sentiment...</span>
              </>
            ) : (
              <>
                <Send className="w-3.5 h-3.5" />
                <span>Analyze Sentiment</span>
              </>
            )}
          </button>
        </div>
      </form>
    </GlassCard>
  );
};
