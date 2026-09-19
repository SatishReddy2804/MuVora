import React from 'react';
import { ShieldCheck, AlertCircle, Cpu } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full border-t border-white/[0.06] bg-surface/50 mt-16 py-8 text-xs text-slate-400">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-brand-cyan" />
            <span className="font-semibold text-slate-200">MuVora AI Engine</span>
            <span>• Bidirectional LSTM + Embedding Layer Architecture</span>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1 text-slate-400">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Zero Review Storage (Client-side Privacy)</span>
            </div>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-white/[0.04] flex flex-col sm:flex-row items-center justify-between gap-2 text-[11px] text-slate-500">
          <p className="flex items-center gap-1">
            <AlertCircle className="w-3.5 h-3.5 text-amber-400/80" />
            The IMDB dataset is primarily English and the trained classifier may not generalize equally to all genres, slang, or culturally specific expressions.
          </p>
          <p>© 2026 MuVora. Academic Major Project Release.</p>
        </div>
      </div>
    </footer>
  );
};
