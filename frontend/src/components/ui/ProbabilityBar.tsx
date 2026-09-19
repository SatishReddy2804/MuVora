import React from 'react';

interface ProbabilityBarProps {
  positiveProbability: number;
  negativeProbability: number;
}

export const ProbabilityBar: React.FC<ProbabilityBarProps> = ({
  positiveProbability,
  negativeProbability,
}) => {
  const posPct = Math.round(positiveProbability * 100);
  const negPct = Math.round(negativeProbability * 100);

  return (
    <div className="w-full space-y-2">
      <div className="flex justify-between items-center text-xs font-semibold">
        <span className="text-sentiment-positive flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-sentiment-positive" />
          Positive {posPct}%
        </span>
        <span className="text-sentiment-negative flex items-center gap-1">
          Negative {negPct}%
          <span className="w-2 h-2 rounded-full bg-sentiment-negative" />
        </span>
      </div>

      {/* Progress track */}
      <div className="w-full h-3 bg-surface-light rounded-full overflow-hidden flex p-[1px]">
        <div
          style={{ width: `${posPct}%` }}
          className="h-full bg-gradient-to-r from-emerald-500 to-sentiment-positive rounded-l-full transition-all duration-700 ease-out"
        />
        <div
          style={{ width: `${negPct}%` }}
          className="h-full bg-gradient-to-r from-rose-500 to-sentiment-negative rounded-r-full transition-all duration-700 ease-out"
        />
      </div>
    </div>
  );
};
