import React from 'react';

interface PhraseChipProps {
  phrase: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  importance?: number;
}

export const PhraseChip: React.FC<PhraseChipProps> = ({
  phrase,
  sentiment,
  importance,
}) => {
  let badgeStyle = 'bg-slate-800/60 text-slate-300 border-slate-700';
  let dotStyle = 'bg-slate-400';

  if (sentiment === 'positive') {
    badgeStyle = 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20';
    dotStyle = 'bg-emerald-400';
  } else if (sentiment === 'negative') {
    badgeStyle = 'bg-rose-500/10 text-rose-300 border-rose-500/20';
    dotStyle = 'bg-rose-400';
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs border ${badgeStyle}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dotStyle}`} />
      <span className="font-medium">{phrase}</span>
      {importance !== undefined && (
        <span className="text-[10px] opacity-70 ml-0.5">
          ({Math.round(importance * 100)}%)
        </span>
      )}
    </span>
  );
};
