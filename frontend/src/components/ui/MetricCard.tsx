import React from 'react';
import { GlassCard } from './GlassCard';

interface MetricCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  icon?: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subtext,
  icon,
}) => {
  return (
    <GlassCard className="p-4 flex flex-col justify-between" hoverEffect>
      <div className="flex items-center justify-between text-slate-400 mb-2">
        <span className="text-xs font-semibold uppercase tracking-wider">{label}</span>
        {icon && <div className="text-brand-cyan">{icon}</div>}
      </div>
      <div>
        <div className="text-2xl font-black tracking-tight text-white">{value}</div>
        {subtext && <div className="text-xs text-slate-400 mt-1">{subtext}</div>}
      </div>
    </GlassCard>
  );
};
