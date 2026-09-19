import React, { useState } from 'react';
import { 
  Sparkles, 
  Clock, 
  Globe, 
  Cpu, 
  ThumbsUp, 
  ThumbsDown, 
  Languages, 
  ArrowRight,
  ShieldCheck,
  Check,
  ChevronDown,
  ChevronUp,
  FileCode,
  Tag,
  Layers,
  HelpCircle
} from 'lucide-react';
import { AnalyzeResponse } from '../../types';
import { GlassCard } from '../ui/GlassCard';
import { ConfidenceRing } from '../ui/ConfidenceRing';
import { ProbabilityBar } from '../ui/ProbabilityBar';
import { SentimentBadge } from '../ui/SentimentBadge';
import { QualityBadge } from '../ui/QualityBadge';
import { PhraseChip } from '../ui/PhraseChip';
import { submitFeedback } from '../../services/api';

interface ResultCardProps {
  result: AnalyzeResponse;
  onReset: () => void;
}

export const ResultCard: React.FC<ResultCardProps> = ({ result, onReset }) => {
  const [feedbackGiven, setFeedbackGiven] = useState<boolean | null>(null);
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false);
  const [showDetectionDetails, setShowDetectionDetails] = useState(false);

  const handleFeedback = async (isHelpful: boolean) => {
    try {
      setIsSubmittingFeedback(true);
      await submitFeedback(result.request_id, isHelpful);
      setFeedbackGiven(isHelpful);
    } catch (e) {
      console.error(e);
    } finally {
      setIsSubmittingFeedback(false);
    }
  };

  const isLowQuality = result.status === 'insufficient_input' || result.status === 'out_of_domain';
  const langDet = result.language_detection;
  const aspects = result.aspects || [];

  return (
    <GlassCard className="w-full space-y-6 relative overflow-hidden border-brand-violet/20 animate-in fade-in zoom-in-95 duration-500">
      {/* Top Banner: Status, Script, & Multilingual Badges */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-white/[0.08]">
        <div className="flex flex-wrap items-center gap-2">
          <SentimentBadge sentiment={result.sentiment} status={result.status} />
          <QualityBadge quality={result.review_quality} />

          {/* Physical Script Badge */}
          {langDet && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-[11px] font-mono bg-white/[0.04] text-slate-300 border border-white/[0.08]">
              <FileCode className="w-3 h-3 text-slate-400" />
              <span>Script: {langDet.script}</span>
            </span>
          )}

          {/* Semantic Language Badge */}
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-[11px] font-semibold bg-brand-cyan/10 text-brand-cyan border border-brand-cyan/30">
            <Globe className="w-3 h-3" />
            <span>Language: {langDet?.semantic_language || result.detected_language}</span>
          </span>

          {/* Transliteration Badge */}
          {langDet?.transliterated && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-[11px] font-semibold bg-brand-violet/15 text-brand-violet border border-brand-violet/30">
              <Languages className="w-3 h-3" />
              <span>Transliterated (Romanized)</span>
            </span>
          )}

          {/* Code-Mixed Badge */}
          {langDet?.code_mixed && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-[11px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30">
              <Layers className="w-3 h-3" />
              <span>Code-Mixed</span>
            </span>
          )}
        </div>

        <div className="flex items-center gap-3 text-xs text-slate-400">
          <span className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5 text-brand-cyan" />
            <span>{result.processing_time_ms} ms</span>
          </span>
        </div>
      </div>

      {/* "Why was this language detected?" Accordion */}
      {langDet && (
        <div className="rounded-xl border border-white/[0.08] bg-white/[0.02] overflow-hidden">
          <button
            type="button"
            onClick={() => setShowDetectionDetails(!showDetectionDetails)}
            className="w-full px-4 py-2.5 flex items-center justify-between text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/[0.02] transition-colors"
          >
            <div className="flex items-center gap-2">
              <HelpCircle className="w-3.5 h-3.5 text-brand-cyan" />
              <span>Why was this detected as {langDet.semantic_language} ({langDet.script} script)?</span>
              <span className="text-[10px] font-normal text-slate-500">
                Confidence: {Math.round(langDet.confidence * 100)}%
              </span>
            </div>
            {showDetectionDetails ? (
              <ChevronUp className="w-4 h-4 text-slate-400" />
            ) : (
              <ChevronDown className="w-4 h-4 text-slate-400" />
            )}
          </button>

          {showDetectionDetails && (
            <div className="p-4 border-t border-white/[0.06] space-y-3 bg-surface-light/30 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-2.5 rounded-lg bg-white/[0.02] border border-white/[0.05]">
                  <span className="text-[10px] uppercase font-bold text-slate-500 block">Physical Writing Script</span>
                  <span className="font-semibold text-white">{langDet.script} ({Math.round(langDet.script_confidence * 100)}%)</span>
                </div>
                <div className="p-2.5 rounded-lg bg-white/[0.02] border border-white/[0.05]">
                  <span className="text-[10px] uppercase font-bold text-slate-500 block">Semantic Language</span>
                  <span className="font-semibold text-brand-cyan">{langDet.semantic_language}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-white/[0.02] border border-white/[0.05]">
                  <span className="text-[10px] uppercase font-bold text-slate-500 block">Detection Methods</span>
                  <span className="text-slate-300 text-[11px]">{langDet.detection_methods.join(', ')}</span>
                </div>
              </div>

              {/* Token-level Language Breakdown */}
              {langDet.token_language_map.length > 0 && (
                <div className="space-y-1.5 pt-1">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                    Token-Level Language Distribution ({langDet.token_language_map.length} tokens):
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {langDet.token_language_map.map((span, idx) => (
                      <span
                        key={idx}
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono border ${
                          span.language === 'te'
                            ? 'bg-brand-cyan/10 text-brand-cyan border-brand-cyan/30'
                            : span.language === 'hi'
                            ? 'bg-brand-violet/10 text-brand-violet border-brand-violet/30'
                            : 'bg-white/[0.04] text-slate-300 border-white/[0.08]'
                        }`}
                        title={`Script: ${span.script}, Lang: ${span.language_name}, Conf: ${Math.round(span.confidence * 100)}%`}
                      >
                        <span className="font-sans font-medium">{span.text}</span>
                        <span className="text-[9px] opacity-70 uppercase">[{span.language}]</span>
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Main Score Section: Confidence Ring + Probabilities */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
        {/* Left: Circular Confidence */}
        <div className="flex flex-col items-center justify-center p-4 bg-white/[0.02] rounded-2xl border border-white/[0.05]">
          <ConfidenceRing
            score={result.confidence}
            sentiment={result.sentiment}
            size={135}
          />
        </div>

        {/* Middle & Right: Probabilities & Overall Tone */}
        <div className="md:col-span-2 space-y-4">
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">
              Neural Probability Distribution
            </span>
            <ProbabilityBar
              positiveProbability={result.positive_probability}
              negativeProbability={result.negative_probability}
            />
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2">
            <div className="p-3 rounded-xl bg-white/[0.02] border border-white/[0.05]">
              <span className="text-[10px] uppercase font-bold text-slate-400 block">Overall Tone</span>
              <span className="text-sm font-semibold text-white capitalize">
                {result.analysis.overall_tone}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-white/[0.02] border border-white/[0.05]">
              <span className="text-[10px] uppercase font-bold text-slate-400 block">Tone Strength</span>
              <span className="text-sm font-semibold text-white capitalize">
                {result.analysis.strength}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Multi-Part Meaning-Based Cinema Narrative Synthesis */}
      <div className={`p-5 rounded-2xl border ${
        isLowQuality 
          ? 'bg-amber-500/10 border-amber-500/20 text-amber-200'
          : 'bg-white/[0.03] border-white/[0.08] text-slate-200'
      } space-y-4`}>
        <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
          <div className="flex items-center gap-2 font-semibold text-xs text-white">
            <Sparkles className="w-4 h-4 text-brand-cyan" />
            <span className="uppercase tracking-wider font-bold">
              Cinema Intelligence Synthesis & Explanation ({result.analysis_display_language?.toUpperCase() || 'EN'})
            </span>
          </div>
          {result.analysis.synthesis?.recommendation && (
            <span className={`text-[11px] font-bold px-3 py-1 rounded-full border ${
              result.sentiment === 'positive'
                ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                : result.sentiment === 'negative'
                ? 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                : 'bg-amber-500/15 text-amber-300 border-amber-500/30'
            }`}>
              {result.analysis.synthesis.recommendation}
            </span>
          )}
        </div>

        {/* Executive Summary */}
        <div className="space-y-1">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
            Executive Summary
          </span>
          <p className="text-sm font-medium text-white leading-relaxed font-sans">
            {result.analysis.synthesis?.executive_summary || result.summary}
          </p>
        </div>

        {/* Detailed Narrative & Reviewer Tone (if detailed analysis available) */}
        {result.analysis.synthesis && !isLowQuality && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 text-xs">
            <div className="p-3 rounded-xl bg-white/[0.02] border border-white/[0.05] space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-brand-cyan block">
                Evidence-Backed Narrative
              </span>
              <p className="text-slate-300 leading-relaxed font-sans">
                {result.analysis.synthesis.detailed_narrative}
              </p>
            </div>
            <div className="p-3 rounded-xl bg-white/[0.02] border border-white/[0.05] space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-brand-violet block">
                Reviewer Tone & Nuance
              </span>
              <p className="text-slate-300 leading-relaxed font-sans">
                {result.analysis.synthesis.reviewer_tone}
              </p>
              {result.analysis.synthesis.limitations && (
                <p className="text-[10px] text-slate-500 italic pt-1">
                  Note: {result.analysis.synthesis.limitations}
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Multilingual Translation Disclosure (if applicable) */}
      {result.translated_review && (
        <div className="p-3.5 rounded-xl bg-brand-violet/[0.06] border border-brand-violet/20 text-xs space-y-1">
          <div className="flex items-center gap-1.5 font-semibold text-brand-violet">
            <Languages className="w-3.5 h-3.5" />
            <span>Normalized to English for BiLSTM Neural Inference:</span>
          </div>
          <p className="text-slate-300 italic font-sans">
            "{result.translated_review}"
          </p>
        </div>
      )}

      {/* Aspect-Based Sentiment Breakdown */}
      {aspects.length > 0 && !isLowQuality && (
        <div className="space-y-3 pt-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
              <Tag className="w-3.5 h-3.5 text-brand-cyan" />
              Aspect-Based Cinema Sentiment
            </span>
            <span className="text-[10px] text-slate-400">
              {aspects.filter(a => a.sentiment !== 'not_mentioned').length} aspect(s) evaluated with context
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {aspects.map((asp) => {
              const isMentioned = asp.sentiment !== 'not_mentioned';
              return (
                <div
                  key={asp.aspect}
                  className={`p-3 rounded-xl border transition-all ${
                    !isMentioned
                      ? 'bg-white/[0.01] border-white/[0.04] opacity-50'
                      : asp.sentiment === 'positive'
                      ? 'bg-emerald-500/[0.06] border-emerald-500/30 ring-1 ring-emerald-500/20'
                      : asp.sentiment === 'negative'
                      ? 'bg-rose-500/[0.06] border-rose-500/30 ring-1 ring-rose-500/20'
                      : 'bg-amber-500/[0.06] border-amber-500/30 ring-1 ring-amber-500/20'
                  }`}
                >
                  <div className="flex justify-between items-start mb-1.5">
                    <span className="font-bold text-xs text-white">{asp.aspect_label}</span>
                    <span
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                        !isMentioned
                          ? 'bg-slate-800 text-slate-400'
                          : asp.sentiment === 'positive'
                          ? 'bg-emerald-500/20 text-emerald-300'
                          : asp.sentiment === 'negative'
                          ? 'bg-rose-500/20 text-rose-300'
                          : 'bg-amber-500/20 text-amber-300'
                      }`}
                    >
                      {asp.sentiment.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>

                  {isMentioned && asp.evidence ? (
                    <div className="mt-2 space-y-1">
                      <p className="text-[11px] text-slate-200 italic border-l-2 border-brand-cyan/40 pl-2">
                        "{asp.evidence}"
                      </p>
                      <span className="text-[9px] text-slate-400 font-mono block">
                        Confidence: {Math.round(asp.confidence * 100)}%
                      </span>
                    </div>
                  ) : (
                    <p className="text-[11px] text-slate-500 italic mt-1">Not mentioned in review</p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Salient Phrases & Signals */}
      {!isLowQuality && (
        <div className="space-y-4 pt-2">
          {result.analysis.key_phrases.length > 0 && (
            <div className="space-y-2">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Salient Key Phrases (Heuristic Extraction)
              </span>
              <div className="flex flex-wrap gap-2">
                {result.analysis.key_phrases.map((kp, idx) => (
                  <PhraseChip
                    key={idx}
                    phrase={kp.phrase}
                    sentiment={kp.sentiment}
                    importance={kp.importance}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Model & Execution Footnote */}
      <div className="pt-4 border-t border-white/[0.08] flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <Cpu className="w-3.5 h-3.5 text-brand-cyan" />
          <span>Model: <strong className="text-slate-200">{result.model.name} v{result.model.version}</strong></span>
          <span className="px-1.5 py-0.2 rounded bg-white/[0.06] text-[10px] uppercase font-mono">{result.model.backend}</span>
        </div>

        {/* Feedback buttons */}
        <div className="flex items-center gap-3">
          <span className="text-slate-500">Was this accurate?</span>
          {feedbackGiven !== null ? (
            <span className="text-emerald-400 flex items-center gap-1 font-medium">
              <Check className="w-3.5 h-3.5" /> Feedback saved
            </span>
          ) : (
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => handleFeedback(true)}
                disabled={isSubmittingFeedback}
                className="p-1.5 rounded-lg bg-white/[0.04] hover:bg-emerald-500/20 hover:text-emerald-300 transition-colors"
                title="Helpful / Accurate"
              >
                <ThumbsUp className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => handleFeedback(false)}
                disabled={isSubmittingFeedback}
                className="p-1.5 rounded-lg bg-white/[0.04] hover:bg-rose-500/20 hover:text-rose-300 transition-colors"
                title="Inaccurate"
              >
                <ThumbsDown className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          <button
            onClick={onReset}
            className="ml-2 px-3 py-1 rounded-lg text-xs font-semibold bg-white/[0.06] hover:bg-white/[0.1] text-white flex items-center gap-1 transition-all"
          >
            <span>Analyze Another</span>
            <ArrowRight className="w-3 h-3" />
          </button>
        </div>
      </div>
    </GlassCard>
  );
};
