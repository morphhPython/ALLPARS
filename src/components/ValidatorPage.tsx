import React, { useState } from 'react';
import { CheckCircle2, ShieldAlert, Sparkles, Filter, Trash2, Download, Search, AlertTriangle, ShieldCheck } from 'lucide-react';
import { RainbowLine, PulseDot } from './RainbowLine';
import { ValidationItem } from '../types';

interface ValidatorPageProps {
  emails: string[];
  validationResults: Record<string, ValidationItem>;
  onBatchValidate: (emailsToValidate: string[]) => void;
  onCleanBase: () => void;
  isValidating: boolean;
  progress: number;
}

export const ValidatorPage: React.FC<ValidatorPageProps> = ({
  emails,
  validationResults,
  onBatchValidate,
  onCleanBase,
  isValidating,
  progress,
}) => {
  const [singleEmailInput, setSingleEmailInput] = useState<string>('');
  const [singleResult, setSingleResult] = useState<ValidationItem | null>(null);
  const [singleLoading, setSingleLoading] = useState<boolean>(false);
  const [activeFilter, setActiveFilter] = useState<'ALL' | 'SAFE' | 'RISKY' | 'TRAP' | 'INVALID'>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const handleSingleInspect = async () => {
    if (!singleEmailInput.trim()) return;
    setSingleLoading(true);
    try {
      const res = await fetch('/api/ai/validate-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: singleEmailInput.trim() }),
      });
      const data = await res.json();
      setSingleResult(data);
    } catch (err: any) {
      setSingleResult({
        email: singleEmailInput,
        status: 'INVALID',
        score: 0,
        detail: `Error: ${err.message}`,
        aiAnalysis: 'Validation failed due to network error.',
      });
    } finally {
      setSingleLoading(false);
    }
  };

  const resultsList = Object.values(validationResults);

  const counts = {
    SAFE: resultsList.filter(r => r.status === 'SAFE').length,
    RISKY: resultsList.filter(r => r.status === 'RISKY').length,
    TRAP: resultsList.filter(r => r.status === 'TRAP').length,
    INVALID: resultsList.filter(r => r.status === 'INVALID').length,
  };

  const filteredResults = resultsList.filter(item => {
    if (activeFilter !== 'ALL' && item.status !== activeFilter) return false;
    if (searchQuery.trim() && !item.email.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-extrabold text-white tracking-wider flex items-center gap-3">
              <CheckCircle2 className="w-7 h-7 text-[#00ff9d]" />
              <span>Gemini AI Email Validator</span>
            </h2>
            <p className="text-xs text-[#8a8aa0] mt-1 font-mono">
              Honeypot detection, MX verification, throwaway domain quarantine, and AI reputation heuristics
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono px-3 py-1.5 rounded-lg bg-[#00f3ff]/10 text-[#00f3ff] border border-[#00f3ff]/30 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Powered by Gemini 3.8</span>
            </span>
          </div>
        </div>
        <RainbowLine className="mt-4" />
      </div>

      {/* Single Email Quick Probe */}
      <div className="glass-panel p-5 rounded-2xl border border-[#8a2be2]/30 space-y-4">
        <label className="text-xs font-mono uppercase text-[#00f3ff] font-bold flex items-center gap-2">
          <Search className="w-3.5 h-3.5" />
          <span>Interactive AI Single Email Inspection</span>
        </label>

        <div className="flex gap-3">
          <input
            type="email"
            value={singleEmailInput}
            onChange={(e) => setSingleEmailInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSingleInspect()}
            placeholder="e.g. spam-trap_99@honeypot.org or developer@gmail.com"
            className="flex-1 bg-[#050508]/90 text-white font-mono text-sm px-4 py-3 rounded-xl border border-[#8a2be2]/35 focus:border-[#00f3ff] outline-none"
          />
          <button
            onClick={handleSingleInspect}
            disabled={singleLoading}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-[#8a2be2] to-[#00f3ff] text-white text-xs font-mono font-bold uppercase tracking-wider flex items-center gap-2 hover:opacity-90 disabled:opacity-50 shrink-0 shadow-[0_0_15px_rgba(0,243,255,0.2)]"
          >
            {singleLoading ? <PulseDot color="cyan" /> : <Sparkles className="w-4 h-4" />}
            <span>{singleLoading ? 'Inspecting with AI...' : 'Inspect with AI'}</span>
          </button>
        </div>

        {/* Single Inspection Result Card */}
        {singleResult && (
          <div
            className={`p-4 rounded-xl border transition-all ${
              singleResult.status === 'SAFE'
                ? 'bg-[#00ff9d]/10 border-[#00ff9d]/40'
                : singleResult.status === 'TRAP'
                ? 'bg-[#ff2a6d]/15 border-[#ff2a6d]/50'
                : singleResult.status === 'RISKY'
                ? 'bg-[#ffcc00]/10 border-[#ffcc00]/40'
                : 'bg-[#8a2be2]/15 border-[#8a2be2]/40'
            }`}
          >
            <div className="flex flex-wrap items-center justify-between gap-3 mb-2">
              <div className="flex items-center gap-2">
                {singleResult.status === 'SAFE' && <ShieldCheck className="w-5 h-5 text-[#00ff9d]" />}
                {singleResult.status === 'TRAP' && <AlertTriangle className="w-5 h-5 text-[#ff2a6d]" />}
                {singleResult.status === 'RISKY' && <AlertTriangle className="w-5 h-5 text-[#ffcc00]" />}
                {singleResult.status === 'INVALID' && <ShieldAlert className="w-5 h-5 text-[#c084fc]" />}
                <span className="font-mono text-sm font-bold text-white">{singleResult.email}</span>
              </div>

              <div className="flex items-center gap-3">
                <span className="text-xs font-mono text-[#8a8aa0]">Deliverability Score:</span>
                <span className="font-mono text-sm font-black text-white px-2 py-0.5 rounded bg-[#050508]/80">
                  {singleResult.score}/100
                </span>
                <span
                  className={`text-xs font-mono font-black px-2.5 py-0.5 rounded uppercase tracking-wider ${
                    singleResult.status === 'SAFE'
                      ? 'bg-[#00ff9d] text-black'
                      : singleResult.status === 'TRAP'
                      ? 'bg-[#ff2a6d] text-white'
                      : singleResult.status === 'RISKY'
                      ? 'bg-[#ffcc00] text-black'
                      : 'bg-[#8a2be2] text-white'
                  }`}
                >
                  {singleResult.status}
                </span>
              </div>
            </div>

            <div className="text-xs font-mono space-y-1 text-[#e0e0e0]">
              <p>
                <strong className="text-[#8a8aa0]">Analysis: </strong>
                {singleResult.detail}
              </p>
              {singleResult.aiAnalysis && (
                <p className="text-[#00f3ff] pt-1">
                  <strong>Gemini AI Insight: </strong>
                  {singleResult.aiAnalysis}
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Batch Database Validation Control */}
      <div className="glass-panel p-5 rounded-2xl border border-[#8a2be2]/30 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <PulseDot color="purple" />
              <span>Full Database Validation ({emails.length} Emails Harvested)</span>
            </h3>
            <p className="text-xs text-[#8a8aa0] font-mono mt-0.5">
              Runs multi-layer syntax, domain MX, honeypot scan, and Gemini AI heuristics across your base
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => onBatchValidate(emails)}
              disabled={isValidating || emails.length === 0}
              className="px-5 py-2.5 rounded-xl bg-[#00ff9d]/20 hover:bg-[#00ff9d]/30 text-[#00ff9d] border border-[#00ff9d]/40 font-mono text-xs font-bold uppercase tracking-wider flex items-center gap-2 disabled:opacity-40"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>{isValidating ? 'Validating...' : 'Validate Base Now'}</span>
            </button>

            <button
              onClick={onCleanBase}
              disabled={isValidating || (counts.TRAP === 0 && counts.INVALID === 0)}
              className="px-4 py-2.5 rounded-xl bg-[#ff2a6d]/20 hover:bg-[#ff2a6d]/30 text-[#ff2a6d] border border-[#ff2a6d]/40 font-mono text-xs font-bold uppercase tracking-wider flex items-center gap-2 disabled:opacity-30"
            >
              <Trash2 className="w-4 h-4" />
              <span>Purge Traps & Invalids ({counts.TRAP + counts.INVALID})</span>
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        {isValidating && (
          <div className="space-y-1 pt-1">
            <div className="flex justify-between text-[11px] font-mono text-[#00f3ff]">
              <span>VERIFYING REPUTATION WITH GEMINI AI...</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full h-2 rounded-full bg-[#050508] border border-[#8a2be2]/30 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-[#8a2be2] via-[#00f3ff] to-[#00ff9d] transition-all duration-200"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Status Breakdown Pills */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
          <div className="p-3 rounded-xl bg-[#00ff9d]/10 border border-[#00ff9d]/30 flex items-center justify-between">
            <span className="text-xs font-mono text-[#8a8aa0]">SAFE:</span>
            <span className="font-mono text-sm font-black text-[#00ff9d]">{counts.SAFE}</span>
          </div>
          <div className="p-3 rounded-xl bg-[#ffcc00]/10 border border-[#ffcc00]/30 flex items-center justify-between">
            <span className="text-xs font-mono text-[#8a8aa0]">RISKY:</span>
            <span className="font-mono text-sm font-black text-[#ffcc00]">{counts.RISKY}</span>
          </div>
          <div className="p-3 rounded-xl bg-[#ff2a6d]/10 border border-[#ff2a6d]/30 flex items-center justify-between">
            <span className="text-xs font-mono text-[#8a8aa0]">TRAP:</span>
            <span className="font-mono text-sm font-black text-[#ff2a6d]">{counts.TRAP}</span>
          </div>
          <div className="p-3 rounded-xl bg-[#8a2be2]/15 border border-[#8a2be2]/30 flex items-center justify-between">
            <span className="text-xs font-mono text-[#8a8aa0]">INVALID:</span>
            <span className="font-mono text-sm font-black text-[#c084fc]">{counts.INVALID}</span>
          </div>
        </div>
      </div>

      {/* Results Table with Filters */}
      <div className="glass-panel p-5 rounded-2xl border border-[#8a2be2]/30 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          {/* Filter Pills */}
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-[#8a8aa0]" />
            {(['ALL', 'SAFE', 'RISKY', 'TRAP', 'INVALID'] as const).map(f => (
              <button
                key={f}
                onClick={() => setActiveFilter(f)}
                className={`px-3 py-1 rounded-lg text-xs font-mono font-bold tracking-wider uppercase transition-all ${
                  activeFilter === f
                    ? 'bg-[#00f3ff]/20 text-[#00f3ff] border border-[#00f3ff]/50'
                    : 'bg-[#050508]/60 text-[#8a8aa0] hover:text-white'
                }`}
              >
                {f}
              </button>
            ))}
          </div>

          <div className="w-64">
            <input
              type="text"
              placeholder="Search in validated list..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#050508] text-xs font-mono px-3 py-1.5 rounded-lg border border-[#8a2be2]/30 text-white placeholder-[#6a6a80] outline-none"
            />
          </div>
        </div>

        <div className="max-h-96 overflow-y-auto rounded-xl border border-[#8a2be2]/25">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-[#050508]/80 text-[#8a8aa0] border-b border-[#8a2be2]/25">
              <tr>
                <th className="p-3">EMAIL ADDRESS</th>
                <th className="p-3">VERDICT</th>
                <th className="p-3">SCORE</th>
                <th className="p-3">AI / HEURISTIC DETAIL</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#8a2be2]/10 bg-[#0c0816]/40">
              {filteredResults.length === 0 ? (
                <tr>
                  <td colSpan={4} className="p-8 text-center text-[#6a6a80]">
                    {resultsList.length === 0
                      ? 'No validated records yet. Click "Validate Base Now" above.'
                      : 'No records matching the selected filter.'}
                  </td>
                </tr>
              ) : (
                filteredResults.map((item, idx) => {
                  const badgeClasses = {
                    SAFE: 'bg-[#00ff9d]/15 text-[#00ff9d] border-[#00ff9d]/30',
                    RISKY: 'bg-[#ffcc00]/15 text-[#ffcc00] border-[#ffcc00]/30',
                    TRAP: 'bg-[#ff2a6d]/20 text-[#ff2a6d] border-[#ff2a6d]/40',
                    INVALID: 'bg-[#8a2be2]/20 text-[#c084fc] border-[#8a2be2]/40',
                  };
                  return (
                    <tr key={idx} className="hover:bg-[#8a2be2]/10 transition-colors">
                      <td className="p-3 text-[#00f3ff] font-semibold">{item.email}</td>
                      <td className="p-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${
                            badgeClasses[item.status]
                          }`}
                        >
                          {item.status}
                        </span>
                      </td>
                      <td className="p-3 text-white font-bold">{item.score}</td>
                      <td className="p-3 text-[#8a8aa0] max-w-md truncate">
                        {item.aiAnalysis || item.detail}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
