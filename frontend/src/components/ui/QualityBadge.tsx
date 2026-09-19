import React from 'react';
import { CheckCircle2, AlertOctagon, HelpCircle } from 'lucide-react';

interface QualityBadgeProps {
  quality: string;
}

export const QualityBadge: React.FC<QualityBadgeProps> = ({ quality }) => {
  const isGood = quality === 'meaningful';

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-[11px] font-medium border ${
        isGood
          ? 'bg-brand-cyan/10 text-brand-cyan border-brand-cyan/30'
          : 'bg-rose-500/10 text-rose-300 border-rose-500/30'
      }`}
    >
      {isGood ? (
        <CheckCircle2 className="w-3 h-3 text-brand-cyan" />
      ) : (
        <AlertOctagon className="w-3 h-3 text-rose-400" />
      )}
      <span>Quality: {quality.replace('_', ' ')}</span>
    </span>
  );
};
