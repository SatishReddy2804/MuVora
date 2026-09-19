import React from 'react';

interface ConfidenceRingProps {
  score: number; // 0.0 to 1.0
  size?: number;
  strokeWidth?: number;
  sentiment?: 'positive' | 'negative' | 'uncertain' | null;
}

export const ConfidenceRing: React.FC<ConfidenceRingProps> = ({
  score,
  size = 130,
  strokeWidth = 10,
  sentiment = 'positive',
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = Math.min(Math.max(score, 0), 1);
  const offset = circumference - progress * circumference;

  let strokeColor = '#22D3EE'; // default cyan
  if (sentiment === 'positive') strokeColor = '#34D399'; // emerald
  else if (sentiment === 'negative') strokeColor = '#FB7185'; // rose
  else if (sentiment === 'uncertain') strokeColor = '#FBBF24'; // amber
  else strokeColor = '#94A3B8'; // neutral

  const percentage = Math.round(progress * 100);

  return (
    <div className="relative flex flex-col items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="rotate-[-90deg]">
        {/* Background track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(255, 255, 255, 0.08)"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        {/* Progress stroke */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={strokeColor}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          fill="transparent"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      {/* Central Value */}
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
        <span className="text-2xl font-black tracking-tight text-white">
          {percentage}%
        </span>
        <span className="text-[10px] uppercase font-bold tracking-widest text-slate-400">
          Confidence
        </span>
      </div>
    </div>
  );
};
