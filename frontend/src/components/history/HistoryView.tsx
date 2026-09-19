import React, { useState } from 'react';
import { Trash2, Film, Clock, Search, ArrowUpDown, Globe, HelpCircle } from 'lucide-react';
import { HistoryItem } from '../../types';
import { GlassCard } from '../ui/GlassCard';
import { SentimentBadge } from '../ui/SentimentBadge';

interface HistoryViewProps {
  history: HistoryItem[];
  onDeleteItem: (id: string) => void;
  onClearHistory: () => void;
  onSelectReview: (item: HistoryItem) => void;
}

export const HistoryView: React.FC<HistoryViewProps> = ({
  history,
  onDeleteItem,
  onClearHistory,
  onSelectReview,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSentiment, setFilterSentiment] = useState<string>('all');

  const filteredHistory = history.filter((item) => {
    const matchesSearch =
      (item.movie_title || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.original_review.toLowerCase().includes(searchTerm.toLowerCase());

    if (!matchesSearch) return false;

    if (filterSentiment === 'all') return true;
    if (filterSentiment === 'inconclusive') {
      return item.status === 'insufficient_input' || item.status === 'out_of_domain';
    }
    return item.sentiment === filterSentiment;
  });

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <span>Session History</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-brand-violet/20 text-brand-violet border border-brand-violet/30 font-normal">
              {history.length} saved
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Analyses stored in your browser session. No data is saved on the server.
          </p>
        </div>

        {history.length > 0 && (
          <button
            onClick={onClearHistory}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold text-rose-400 hover:text-rose-300 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 flex items-center gap-1.5 transition-all"
          >
            <Trash2 className="w-3.5 h-3.5" />
            Clear All History
          </button>
        )}
      </div>

      {history.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {/* Search bar */}
          <div className="sm:col-span-2 relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by movie title or review text..."
              className="w-full pl-9 pr-3.5 py-2 rounded-xl bg-surface-light/70 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-cyan"
            />
          </div>

          {/* Filter dropdown */}
          <div>
            <select
              value={filterSentiment}
              onChange={(e) => setFilterSentiment(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-surface-light/70 border border-white/10 text-xs text-white focus:outline-none focus:border-brand-violet"
            >
              <option value="all">All Sentiments</option>
              <option value="positive">Positive Only</option>
              <option value="negative">Negative Only</option>
              <option value="uncertain">Uncertain Only</option>
              <option value="inconclusive">Inconclusive / Low Quality</option>
            </select>
          </div>
        </div>
      )}

      {/* History List or Empty State */}
      {filteredHistory.length === 0 ? (
        <GlassCard className="text-center py-12 space-y-3">
          <div className="w-12 h-12 rounded-2xl bg-white/[0.04] border border-white/[0.08] mx-auto flex items-center justify-center text-slate-500">
            <Film className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-bold text-slate-200">No Analysis Records Found</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            {history.length === 0
              ? 'Submit your first movie review in the Analyzer tab to begin tracking history.'
              : 'No results match your search and filter criteria.'}
          </p>
        </GlassCard>
      ) : (
        <div className="space-y-3">
          {filteredHistory.map((item) => (
            <GlassCard
              key={item.request_id}
              className="p-4 hover:border-brand-violet/30 transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 group"
            >
              <div 
                onClick={() => onSelectReview(item)}
                className="cursor-pointer flex-1 space-y-1.5"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-bold text-sm text-white group-hover:text-brand-cyan transition-colors">
                    {item.movie_title || 'Untitled Movie Review'}
                  </span>
                  <SentimentBadge sentiment={item.sentiment} status={item.status} />
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-white/[0.04] text-slate-400 border border-white/[0.06]">
                    {item.detected_language}
                  </span>
                </div>

                <p className="text-xs text-slate-300 line-clamp-2 italic">
                  "{item.original_review}"
                </p>

                <div className="flex items-center gap-3 text-[10px] text-slate-500">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(item.saved_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                  <span>•</span>
                  <span>Confidence: {Math.round(item.confidence * 100)}%</span>
                  <span>•</span>
                  <span>{item.processing_time_ms} ms</span>
                </div>
              </div>

              <div className="flex items-center gap-2 self-end sm:self-center">
                <button
                  onClick={() => onSelectReview(item)}
                  className="px-2.5 py-1 rounded-lg text-xs font-medium bg-white/[0.06] hover:bg-brand-violet/20 hover:text-brand-violet border border-white/[0.06] transition-colors"
                >
                  View Details
                </button>
                <button
                  onClick={() => onDeleteItem(item.request_id)}
                  className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                  title="Delete from history"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </GlassCard>
          ))}
        </div>
      )}
    </div>
  );
};
