import React from 'react';
import { Sparkles, History, LineChart, Info, Film, Languages } from 'lucide-react';

interface NavbarProps {
  activeTab: 'analyzer' | 'translator' | 'history' | 'insights' | 'about';
  setActiveTab: (tab: 'analyzer' | 'translator' | 'history' | 'insights' | 'about') => void;
  historyCount: number;
  isBackendHealthy: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  historyCount,
  isBackendHealthy,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-white/[0.08] bg-background/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div 
          onClick={() => setActiveTab('analyzer')} 
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-brand-violet to-brand-cyan p-[1px]">
            <div className="w-full h-full bg-surface rounded-xl flex items-center justify-center group-hover:bg-opacity-80 transition-all">
              <Film className="w-5 h-5 text-brand-cyan group-hover:scale-110 transition-transform" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-brand-cyan">
                MuVora
              </span>
              <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full bg-brand-violet/20 text-brand-violet border border-brand-violet/30">
                AI NLP
              </span>
            </div>
            <p className="text-[10px] text-slate-400 hidden sm:block">
              Multilingual Film Sentiment Intelligence
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 sm:gap-2">
          <button
            onClick={() => setActiveTab('analyzer')}
            className={`flex items-center gap-2 px-3 sm:px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'analyzer'
                ? 'bg-white/10 text-white shadow-sm border border-white/10'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Sparkles className="w-4 h-4 text-brand-cyan" />
            <span>Analyzer</span>
          </button>

          <button
            onClick={() => setActiveTab('translator')}
            className={`flex items-center gap-2 px-3 sm:px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'translator'
                ? 'bg-white/10 text-white shadow-sm border border-white/10'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Languages className="w-4 h-4 text-brand-violet" />
            <span>Translator</span>
          </button>

          <button
            onClick={() => setActiveTab('history')}
            className={`flex items-center gap-2 px-3 sm:px-4 py-2 rounded-lg text-sm font-medium transition-all relative ${
              activeTab === 'history'
                ? 'bg-white/10 text-white shadow-sm border border-white/10'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <History className="w-4 h-4 text-brand-violet" />
            <span>History</span>
            {historyCount > 0 && (
              <span className="ml-1 text-xs px-1.5 py-0.2 rounded-full bg-brand-violet text-white">
                {historyCount}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab('insights')}
            className={`flex items-center gap-2 px-3 sm:px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'insights'
                ? 'bg-white/10 text-white shadow-sm border border-white/10'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <LineChart className="w-4 h-4 text-emerald-400" />
            <span>Model Insights</span>
          </button>

          <button
            onClick={() => setActiveTab('about')}
            className={`flex items-center gap-2 px-3 sm:px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'about'
                ? 'bg-white/10 text-white shadow-sm border border-white/10'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Info className="w-4 h-4 text-slate-300" />
            <span>About</span>
          </button>
        </nav>

        {/* System Health Indicator */}
        <div className="hidden md:flex items-center gap-2 text-xs text-slate-400 px-3 py-1.5 rounded-full bg-white/[0.04] border border-white/[0.06]">
          <span className={`w-2 h-2 rounded-full ${isBackendHealthy ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
          <span>{isBackendHealthy ? 'BiLSTM Core Online' : 'Connecting...'}</span>
        </div>
      </div>
    </header>
  );
};
