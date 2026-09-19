import React from 'react';
import { ShieldCheck, Globe, Cpu, AlertTriangle, BookOpen, Layers } from 'lucide-react';
import { GlassCard } from '../ui/GlassCard';

export const AboutView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white">About MuVora & NLP Methodology</h2>
        <p className="text-xs text-slate-400 mt-1">
          A high-performance deep learning platform for multilingual cinema sentiment intelligence.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <GlassCard className="space-y-3">
          <div className="flex items-center gap-2 pb-2 border-b border-white/[0.08]">
            <Globe className="w-4 h-4 text-brand-cyan" />
            <h3 className="text-sm font-bold text-white">Multilingual Architecture</h3>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            The Stanford IMDB benchmark dataset is primarily an English dataset. Rather than making false claims that an English-trained model understands non-English tokens natively, MuVora uses a principled multi-stage pipeline:
          </p>
          <ol className="list-decimal list-inside text-xs text-slate-400 space-y-1.5 pl-1">
            <li><strong className="text-slate-200">Script & Language Detection:</strong> Inspects Unicode script blocks (Devanagari, Telugu, Tamil, Malayalam, Bengali, etc.) and n-gram profiles.</li>
            <li><strong className="text-slate-200">Translation Service Abstraction:</strong> Non-English reviews are translated into English for reliable feature representation.</li>
            <li><strong className="text-slate-200">BiLSTM Inference:</strong> Neural classification occurs on the normalized English representation.</li>
            <li><strong className="text-slate-200">Localized Explanation:</strong> The final summary is synthesized back in the user's original language using localized templates.</li>
          </ol>
        </GlassCard>

        <GlassCard className="space-y-3">
          <div className="flex items-center gap-2 pb-2 border-b border-white/[0.08]">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-bold text-white">Input Quality & Smash Guard</h3>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Standard sentiment classifiers force arbitrary positive/negative labels on random keyboard smash (such as <code className="text-brand-cyan">hsfiiwjhfoiowfohwoehfhw</code>). MuVora incorporates a multi-signal quality validator:
          </p>
          <ul className="list-disc list-inside text-xs text-slate-400 space-y-1.5 pl-1">
            <li>Shannon entropy & character repetition ratios.</li>
            <li>Vowel-to-consonant clustering detection.</li>
            <li>Punctuation and symbol-only filters.</li>
            <li>Preserves legitimate short reviews (e.g. <em>"Amazing!"</em>, <em>"Worst movie ever."</em>, <em>"చాలా బాగుంది"</em>, <em>"बहुत अच्छी फिल्म"</em>).</li>
          </ul>
        </GlassCard>
      </div>

      {/* Dataset limitations warning */}
      <div className="p-4 rounded-2xl bg-amber-500/[0.08] border border-amber-500/25 space-y-2">
        <div className="flex items-center gap-2 text-amber-300 font-bold text-xs">
          <AlertTriangle className="w-4 h-4" />
          <span>Responsible AI & Benchmark Dataset Limitations</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          The IMDB dataset is primarily English and the trained classifier may not generalize equally to all languages, genres, review lengths, slang, sarcasm, or culturally specific expressions. Model predictions should be regarded as probabilistic decision aids rather than definitive human judgments.
        </p>
      </div>

      <GlassCard className="space-y-3">
        <div className="flex items-center gap-2 pb-2 border-b border-white/[0.08]">
          <BookOpen className="w-4 h-4 text-brand-violet" />
          <h3 className="text-sm font-bold text-white">Privacy & Session Data Handling</h3>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          MuVora is engineered with privacy-by-design. Submitted reviews are processed strictly in ephemeral memory during inference and are never logged or stored in a server database. History is maintained solely inside your browser's local storage and can be completely wiped at any time with a single click.
        </p>
      </GlassCard>
    </div>
  );
};
