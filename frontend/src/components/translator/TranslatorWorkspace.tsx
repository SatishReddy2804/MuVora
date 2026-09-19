import React, { useState, useEffect, useRef } from 'react';
import { 
  Languages, 
  ArrowRightLeft, 
  Copy, 
  Check, 
  RotateCcw, 
  Sparkles, 
  Send, 
  Globe, 
  Mic, 
  MicOff, 
  Volume2, 
  Download, 
  Image as ImageIcon 
} from 'lucide-react';
import { GlassCard } from '../ui/GlassCard';
import { translateText, getSupportedLanguages } from '../../services/api';
import { SupportedLanguageItem } from '../../types';

export const TranslatorWorkspace: React.FC = () => {
  const [text, setText] = useState('');
  const [sourceLang, setSourceLang] = useState('auto');
  const [targetLangs, setTargetLangs] = useState<string[]>(['en', 'te', 'hi']);
  const [translations, setTranslations] = useState<Record<string, string>>({});
  const [detectedSource, setDetectedSource] = useState<string | null>(null);
  const [detectedSourceName, setDetectedSourceName] = useState<string | null>(null);
  const [isTransliterated, setIsTransliterated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [availableLanguages, setAvailableLanguages] = useState<SupportedLanguageItem[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [speakingKey, setSpeakingKey] = useState<string | null>(null);

  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    getSupportedLanguages()
      .then((res) => setAvailableLanguages(res.languages))
      .catch((err) => console.error(err));
  }, []);

  const handleTranslate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!text.trim()) {
      setError('Please enter text to translate.');
      return;
    }
    setError(null);
    setIsLoading(true);

    try {
      const res = await translateText({
        text: text.trim(),
        source_language: sourceLang,
        target_languages: targetLangs,
      });

      setTranslations(res.translations);
      setDetectedSource(res.detected_source);
      setDetectedSourceName(res.detected_source_name);
      setIsTransliterated(res.is_transliterated);
    } catch (err: any) {
      setError(err.message || 'Translation failed.');
    } finally {
      setIsLoading(false);
    }
  };

  // Speech Recognition (Web Speech API)
  const toggleSpeechRecognition = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError('Speech recognition is not supported in this browser. Please try Chrome or Edge.');
      return;
    }

    if (isListening) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsListening(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      
      // Determine speech recognition language
      if (sourceLang === 'te') recognition.lang = 'te-IN';
      else if (sourceLang === 'hi') recognition.lang = 'hi-IN';
      else if (sourceLang === 'ta') recognition.lang = 'ta-IN';
      else recognition.lang = 'en-US';

      recognition.onstart = () => setIsListening(true);
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setText((prev) => (prev ? `${prev} ${transcript}` : transcript));
        setIsListening(false);
      };
      recognition.onerror = (event: any) => {
        console.warn('Speech recognition error:', event.error);
        setIsListening(false);
      };
      recognition.onend = () => setIsListening(false);

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.error(err);
      setIsListening(false);
    }
  };

  // Text-To-Speech Pronunciation (Web SpeechSynthesis API)
  const handleSpeak = (spokenText: string, langCode: string, keyId: string) => {
    if (!('speechSynthesis' in window)) {
      setError('Speech synthesis is not supported in this browser.');
      return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(spokenText);
    
    // Map language tag
    if (langCode === 'te') utterance.lang = 'te-IN';
    else if (langCode === 'hi') utterance.lang = 'hi-IN';
    else if (langCode === 'ta') utterance.lang = 'ta-IN';
    else if (langCode === 'es') utterance.lang = 'es-ES';
    else utterance.lang = 'en-US';

    utterance.onstart = () => setSpeakingKey(keyId);
    utterance.onend = () => setSpeakingKey(null);
    utterance.onerror = () => setSpeakingKey(null);

    window.speechSynthesis.speak(utterance);
  };

  const handleCopy = (key: string, content: string) => {
    navigator.clipboard.writeText(content);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const handleDownload = () => {
    if (!text && Object.keys(translations).length === 0) return;
    
    let content = `--- MUVORA TRANSLATION EXPORT ---\n\n`;
    content += `[Original Input (${sourceLang})]:\n${text}\n\n`;
    content += `[Translations]:\n`;
    for (const [code, val] of Object.entries(translations)) {
      content += `\n--- ${code.toUpperCase()} ---\n${val}\n`;
    }

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `muvora_translation_${Date.now()}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleSwap = () => {
    if (targetLangs.length > 0 && sourceLang !== 'auto') {
      const firstTarget = targetLangs[0];
      const oldSource = sourceLang;
      const translatedVal = translations[firstTarget];
      
      setSourceLang(firstTarget);
      setTargetLangs([oldSource, ...targetLangs.slice(1)]);
      if (translatedVal) {
        setText(translatedVal);
        setTranslations({ [oldSource]: text });
      }
    }
  };

  const toggleTargetLang = (code: string) => {
    if (targetLangs.includes(code)) {
      if (targetLangs.length > 1) {
        setTargetLangs(targetLangs.filter((l) => l !== code));
      }
    } else {
      if (targetLangs.length < 5) {
        setTargetLangs([...targetLangs, code]);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Languages className="w-5 h-5 text-brand-cyan" />
            <span>Google-Style Multilingual Translation Workspace</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real multi-target translation, auto-detection, voice input, audio pronunciation, and clean export.
          </p>
        </div>

        {Object.keys(translations).length > 0 && (
          <button
            onClick={handleDownload}
            className="px-3 py-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-slate-300 hover:text-white border border-white/[0.08] text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-brand-cyan" />
            <span>Export Translation</span>
          </button>
        )}
      </div>

      <GlassCard className="space-y-5">
        {/* Controls Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-white/[0.08]">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-400">Source:</span>
            <select
              value={sourceLang}
              onChange={(e) => setSourceLang(e.target.value)}
              className="px-3 py-1.5 rounded-lg bg-surface-light border border-white/10 text-xs text-white focus:outline-none focus:border-brand-cyan"
            >
              <option value="auto">🌐 Auto Detect</option>
              {availableLanguages.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.name} ({l.native_name})
                </option>
              ))}
            </select>

            <button
              onClick={handleSwap}
              disabled={sourceLang === 'auto'}
              className="p-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-slate-400 hover:text-white border border-white/[0.06] transition-colors disabled:opacity-30"
              title="Swap Languages"
            >
              <ArrowRightLeft className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Target Languages selector */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-xs font-semibold text-slate-400 mr-1">Target(s):</span>
            {['en', 'te', 'hi', 'ta', 'es'].map((code) => {
              const lang = availableLanguages.find((l) => l.code === code) || { name: code, native_name: code };
              const isSelected = targetLangs.includes(code);
              return (
                <button
                  key={code}
                  type="button"
                  onClick={() => toggleTargetLang(code)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-medium border transition-all ${
                    isSelected
                      ? 'bg-brand-violet/20 text-brand-violet border-brand-violet/40 font-semibold'
                      : 'bg-white/[0.02] text-slate-400 border-white/[0.06] hover:bg-white/[0.06]'
                  }`}
                >
                  {lang.name}
                </button>
              );
            })}
          </div>
        </div>

        {/* Input & Output Side-by-Side */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Source Text Area */}
          <div className="space-y-2 relative">
            <div className="flex justify-between items-center text-xs">
              <span className="font-semibold text-slate-300">Original Review / Text:</span>
              <span className="text-slate-500 font-mono">{text.length} chars</span>
            </div>

            <div className="relative">
              <textarea
                value={text}
                onChange={(e) => {
                  setText(e.target.value);
                  if (error) setError(null);
                }}
                placeholder="Enter review or opinion in English, Telugu, Hindi, or Romanized (e.g. 'The movie is awesome', 'సినిమా బాగుంది', or 'cinema chala bagundhi')..."
                rows={7}
                className="w-full px-4 py-3 pb-10 rounded-xl bg-surface-light/70 border border-white/10 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-cyan font-sans"
              />

              {/* In-box controls (Speech input + Audio playback) */}
              <div className="absolute bottom-2.5 left-3 right-3 flex justify-between items-center">
                <div className="flex items-center gap-1.5">
                  {/* Voice input button */}
                  <button
                    type="button"
                    onClick={toggleSpeechRecognition}
                    className={`p-1.5 rounded-lg border transition-all flex items-center gap-1 text-xs ${
                      isListening
                        ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 animate-pulse'
                        : 'bg-white/[0.06] hover:bg-white/[0.12] text-slate-400 hover:text-white border-white/[0.08]'
                    }`}
                    title={isListening ? 'Stop listening' : 'Speak / Voice Input'}
                  >
                    {isListening ? <MicOff className="w-3.5 h-3.5 text-rose-400" /> : <Mic className="w-3.5 h-3.5" />}
                    <span className="text-[10px]">{isListening ? 'Listening...' : 'Voice'}</span>
                  </button>

                  {/* Audio Listen TTS */}
                  {text && (
                    <button
                      type="button"
                      onClick={() => handleSpeak(text, sourceLang, 'source')}
                      className={`p-1.5 rounded-lg border transition-all text-slate-400 hover:text-white ${
                        speakingKey === 'source'
                          ? 'bg-brand-cyan/20 text-brand-cyan border-brand-cyan/40 animate-pulse'
                          : 'bg-white/[0.06] hover:bg-white/[0.12] border-white/[0.08]'
                      }`}
                      title="Listen to original text"
                    >
                      <Volume2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                {text && (
                  <button
                    type="button"
                    onClick={() => handleCopy('source', text)}
                    className="p-1.5 rounded-lg bg-white/[0.06] hover:bg-white/[0.12] text-slate-400 hover:text-white border border-white/[0.08] transition-colors"
                    title="Copy input text"
                  >
                    {copiedKey === 'source' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  </button>
                )}
              </div>
            </div>

            {/* Transliteration badge if detected */}
            {detectedSource && (
              <div className="flex items-center gap-2 text-xs pt-1">
                <span className="text-slate-400">Detected:</span>
                <span className="px-2 py-0.5 rounded bg-brand-cyan/10 text-brand-cyan border border-brand-cyan/30 font-semibold">
                  {detectedSourceName || detectedSource}
                </span>
                {isTransliterated && (
                  <span className="px-2 py-0.5 rounded bg-brand-violet/10 text-brand-violet border border-brand-violet/30 font-medium">
                    Transliterated (Romanized Script)
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Translations Output */}
          <div className="space-y-2">
            <span className="text-xs font-semibold text-slate-300 block">
              Translated Output ({targetLangs.length} target language{targetLangs.length > 1 ? 's' : ''}):
            </span>

            <div className="space-y-3 max-h-[350px] overflow-y-auto pr-1">
              {Object.keys(translations).length === 0 ? (
                <div className="h-44 rounded-xl border border-dashed border-white/10 flex flex-col items-center justify-center text-slate-500 text-xs space-y-1">
                  <Globe className="w-6 h-6 mb-1 opacity-50 text-brand-cyan" />
                  <span className="font-semibold text-slate-400">Ready for Multilingual Translation</span>
                  <span className="text-[11px] text-slate-500">Supports English, Telugu, Hindi, Tamil, and more</span>
                </div>
              ) : (
                targetLangs.map((tCode) => {
                  const langMeta = availableLanguages.find((l) => l.code === tCode);
                  const translation = translations[tCode] || 'Processing...';
                  return (
                    <div
                      key={tCode}
                      className="p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.08] space-y-2 group transition-all hover:border-white/[0.15]"
                    >
                      <div className="flex justify-between items-center text-xs">
                        <span className="font-semibold text-brand-cyan flex items-center gap-1.5">
                          <span>{langMeta?.name || tCode}</span>
                          <span className="text-slate-500 font-normal">({langMeta?.native_name})</span>
                        </span>
                        
                        <div className="flex items-center gap-1">
                          {/* Audio pronunciation */}
                          <button
                            onClick={() => handleSpeak(translation, tCode, tCode)}
                            className={`p-1 rounded text-slate-400 hover:text-white transition-colors ${
                              speakingKey === tCode ? 'text-brand-cyan animate-pulse' : ''
                            }`}
                            title="Listen pronunciation"
                          >
                            <Volume2 className="w-3.5 h-3.5" />
                          </button>

                          {/* Copy */}
                          <button
                            onClick={() => handleCopy(tCode, translation)}
                            className="text-slate-400 hover:text-white p-1 rounded transition-colors"
                            title="Copy translation"
                          >
                            {copiedKey === tCode ? (
                              <Check className="w-3.5 h-3.5 text-emerald-400" />
                            ) : (
                              <Copy className="w-3.5 h-3.5" />
                            )}
                          </button>
                        </div>
                      </div>

                      <p className="text-sm text-slate-100 leading-relaxed font-sans select-all">
                        {translation}
                      </p>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>

        {error && <p className="text-xs text-rose-400">{error}</p>}

        {/* Action Buttons */}
        <div className="flex items-center justify-between pt-3 border-t border-white/[0.06]">
          <button
            type="button"
            onClick={() => {
              setText('');
              setTranslations({});
              setDetectedSource(null);
            }}
            className="px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white bg-white/[0.04] border border-white/[0.06] flex items-center gap-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Clear
          </button>

          <button
            onClick={() => handleTranslate()}
            disabled={isLoading || !text.trim()}
            className="px-6 py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider text-white bg-gradient-to-r from-brand-violet to-brand-cyan hover:opacity-95 shadow-lg shadow-brand-violet/20 flex items-center gap-2 transition-all disabled:opacity-50"
          >
            {isLoading ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Translating...</span>
              </>
            ) : (
              <>
                <Send className="w-3.5 h-3.5" />
                <span>Translate Review</span>
              </>
            )}
          </button>
        </div>
      </GlassCard>
    </div>
  );
};

