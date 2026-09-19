import React from 'react';
import { ThumbsUp, ThumbsDown, HelpCircle, AlertTriangle } from 'lucide-react';
import { SentimentType, AnalysisStatus } from '../../types';

interface SentimentBadgeProps {
  sentiment: SentimentType;
  status: AnalysisStatus;
}

export const SentimentBadge: React.FC<SentimentBadgeProps> = ({ sentiment, status }) => {
  if (status === 'insufficient_input' || status === 'out_of_domain') {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30">
        <AlertTriangle className="w-3.5 h-3.5" />
        Inconclusive Input
      </span>
    );
  }

  if (sentiment === 'positive') {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
        <ThumbsUp className="w-3.5 h-3.5" />
        Positive Sentiment
      </span>
    );
  }

  if (sentiment === 'negative') {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/15 text-rose-400 border border-rose-500/30">
        <ThumbsDown className="w-3.5 h-3.5" />
        Negative Sentiment
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30">
      <HelpCircle className="w-3.5 h-3.5" />
      Uncertain / Mixed
    </span>
  );
};
