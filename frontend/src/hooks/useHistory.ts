import { useState, useEffect } from 'react';
import { AnalyzeResponse, HistoryItem } from '../types';

const STORAGE_KEY = 'muvora_sentiment_history_v1';

export function useHistory() {
  const [history, setHistory] = useState<HistoryItem[]>([]);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        setHistory(JSON.parse(stored));
      }
    } catch (e) {
      console.error('Failed to load history from localStorage', e);
    }
  }, []);

  const addHistory = (item: AnalyzeResponse) => {
    const newItem: HistoryItem = {
      ...item,
      saved_at: new Date().toISOString(),
    };
    setHistory((prev) => {
      // Keep up to 50 most recent
      const updated = [newItem, ...prev.filter(h => h.request_id !== item.request_id)].slice(0, 50);
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      } catch (e) {
        console.error('Failed to save item to localStorage', e);
      }
      return updated;
    });
  };

  const deleteHistoryItem = (requestId: string) => {
    setHistory((prev) => {
      const updated = prev.filter(h => h.request_id !== requestId);
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      } catch (e) {
        console.error('Failed to update localStorage', e);
      }
      return updated;
    });
  };

  const clearHistory = () => {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (e) {
      console.error('Failed to clear localStorage', e);
    }
    setHistory([]);
  };

  return {
    history,
    addHistory,
    deleteHistoryItem,
    clearHistory,
  };
}
