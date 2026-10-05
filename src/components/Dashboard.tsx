import React from 'react';
import { Play, Infinity as InfinityIcon, Square, Trash2, ArrowUpRight, ShieldCheck, Mail, Database } from 'lucide-react';
import { RainbowLine, PulseDot } from './RainbowLine';
import { CrawlerStatus } from '../types';

interface DashboardProps {
  status: CrawlerStatus;
  totalEmails: number;
  personalEmails: number;
  recentEmails: { email: string; source: string; time: string }[];
  onStartSingle: () => void;
  onStartInfinite: () => void;
  onStop: () => void;
  onClear: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  status,
  totalEmails,
  personalEmails,
  recentEmails,
  onStartSingle,
  onStartInfinite,
  onStop,
  onClear,
}) => {
  return (
    <div className="space-y-6">
      {/* Page Title */}
      <div>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-extrabold text-white tracking-wider flex items-center gap-3">
              <span>Control Dashboard</span>
              <span className="text-xs px-2.5 py-1 rounded-full bg-[#00f3ff]/10 text-[#00f3ff] border border-[#00f3ff]/30 font-mono font-normal">
                SYSTEM LIVE
              </span>
            </h2>
            <p className="text-xs text-[#8a8aa0] mt-1 font-mono">
              Autonomous OSINT harvesting, recursive spidering, and AI deliverability pipeline
            </p>
          </div>
        </div>
        <RainbowLine className="mt-4" />
      </div>

      {/* Top 4 Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Total Emails */}
        <div className="glass-panel p-5 rounded-2xl relative overflow-hidden border-l-4 border-l-[#00f3ff] group transition-all">
          <div className="flex items-center justify-between text-[#8a8aa0] mb-2">
            <span className="text-xs font-mono uppercase tracking-wider">Harvested Mails</span>
            <Database className="w-4 h-4 text-[#00f3ff]" />
          </div>
          <div className="text-4xl font-extrabold text-[#00f3ff] font-mono tracking-tight drop-shadow-[0_0_12px_rgba(0,243,255,0.4)]">
            {totalEmails}
          </div>
          <div className="text-[11px] text-[#6a6a80] mt-2 font-mono flex items-center justify-between">
            <span>TXT Database: active</span>
            <span className="text-[#00ff9d]">100% deduplicated</span>
          </div>
        </div>

        {/* Card 2: Personal Mailboxes */}
        <div className="glass-panel p-5 rounded-2xl relative overflow-hidden border-l-4 border-l-[#00ff9d] group transition-all">
          <div className="flex items-center justify-between text-[#8a8aa0] mb-2">
            <span className="text-xs font-mono uppercase tracking-wider">Personal (Human)</span>
            <Mail className="w-4 h-4 text-[#00ff9d]" />
          </div>
          <div className="text-4xl font-extrabold text-[#00ff9d] font-mono tracking-tight drop-shadow-[0_0_12px_rgba(0,255,157,0.4)]">
            {personalEmails}
          </div>
          <div className="text-[11px] text-[#6a6a80] mt-2 font-mono">
            Gmail, Yandex, Mail.ru, Yahoo
          </div>
        </div>

        {/* Card 3: Engine State */}
        <div className="glass-panel p-5 rounded-2xl relative overflow-hidden border-l-4 border-l-[#b026ff] group transition-all">
          <div className="flex items-center justify-between text-[#8a8aa0] mb-2">
            <span className="text-xs font-mono uppercase tracking-wider">Crawler Engine</span>
            <PulseDot color={status.running ? 'green' : 'purple'} active={status.running} />
          </div>
          <div className={`text-3xl font-extrabold font-mono tracking-tight ${status.running ? 'text-[#00ff9d]' : 'text-[#c084fc]'}`}>
            {status.running ? (status.infinite ? 'INFINITE' : 'BATCH RUN') : 'STANDBY'}
          </div>
          <div className="text-[11px] text-[#6a6a80] mt-2 font-mono">
            {status.running ? `Crawled: ${status.pagesCrawled} pages` : 'Awaiting launch command'}
          </div>
        </div>

        {/* Card 4: Target & Queue */}
        <div className="glass-panel p-5 rounded-2xl relative overflow-hidden border-l-4 border-l-[#ffcc00] group transition-all">
          <div className="flex items-center justify-between text-[#8a8aa0] mb-2">
            <span className="text-xs font-mono uppercase tracking-wider">Queue & Spider</span>
            <span className="text-xs font-mono text-[#ffcc00]">{status.queueSize} URLs</span>
          </div>
          <div className="text-sm font-mono text-[#e0e0e0] truncate mt-1">
            {status.currentTarget || 'Idle (no active request)'}
          </div>
          <div className="text-[11px] text-[#6a6a80] mt-2 font-mono flex items-center justify-between">
            <span>Visited nodes:</span>
            <span className="text-[#00f3ff]">{status.visitedCount}</span>
          </div>
        </div>
      </div>

      {/* Control Deck */}
      <div className="glass-panel p-6 rounded-2xl border border-[#8a2be2]/30 space-y-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <PulseDot color="cyan" />
            <h3 className="text-base font-bold text-white tracking-wide">Mission Control Deck</h3>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono text-[#8a8aa0]">
            <ShieldCheck className="w-4 h-4 text-[#00ff9d]" />
            <span>Anti-Crash Sandboxed Engine</span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
          <button
            onClick={onStartSingle}
            disabled={status.running}
            className="flex items-center justify-center gap-2.5 px-5 py-3.5 rounded-xl font-bold text-xs uppercase tracking-wider transition-all bg-[#00f3ff]/15 hover:bg-[#00f3ff]/25 text-[#00f3ff] border border-[#00f3ff]/40 disabled:opacity-30 disabled:cursor-not-allowed shadow-[0_0_15px_rgba(0,243,255,0.15)]"
          >
            <Play className="w-4 h-4" />
            <span>Run Single Batch (40p)</span>
          </button>

          <button
            onClick={onStartInfinite}
            disabled={status.running}
            className="flex items-center justify-center gap-2.5 px-5 py-3.5 rounded-xl font-bold text-xs uppercase tracking-wider transition-all bg-[#00ff9d]/15 hover:bg-[#00ff9d]/25 text-[#00ff9d] border border-[#00ff9d]/40 disabled:opacity-30 disabled:cursor-not-allowed shadow-[0_0_15px_rgba(0,255,157,0.15)]"
          >
            <InfinityIcon className="w-4 h-4" />
            <span>Enable Infinite Spider</span>
          </button>

          <button
            onClick={onStop}
            disabled={!status.running}
            className="flex items-center justify-center gap-2.5 px-5 py-3.5 rounded-xl font-bold text-xs uppercase tracking-wider transition-all bg-[#ff2a6d]/20 hover:bg-[#ff2a6d]/30 text-[#ff2a6d] border border-[#ff2a6d]/40 disabled:opacity-30 disabled:cursor-not-allowed shadow-[0_0_15px_rgba(255,42,109,0.15)]"
          >
            <Square className="w-4 h-4" />
            <span>Kill Process Engine</span>
          </button>

          <button
            onClick={onClear}
            className="flex items-center justify-center gap-2.5 px-5 py-3.5 rounded-xl font-bold text-xs uppercase tracking-wider transition-all bg-[#8a2be2]/15 hover:bg-[#8a2be2]/25 text-[#c084fc] border border-[#8a2be2]/40"
          >
            <Trash2 className="w-4 h-4" />
            <span>Clear Harvest Cache</span>
          </button>
        </div>

        {/* Animated Progress Chunk */}
        <div className="space-y-1.5 pt-2">
          <div className="flex justify-between text-[11px] font-mono text-[#8a8aa0]">
            <span>ENGINE ACTIVITY STREAM</span>
            <span>{status.running ? 'RUNNING RECURSIVE CRAWL' : 'PAUSED'}</span>
          </div>
          <div className="w-full h-2.5 rounded-full bg-[#050508] border border-[#8a2be2]/30 overflow-hidden relative">
            <div
              className={`h-full transition-all duration-300 ${
                status.running
                  ? 'w-full bg-gradient-to-r from-[#8a2be2] via-[#00f3ff] to-[#00ff9d] animate-pulse'
                  : 'w-0'
              }`}
            />
          </div>
        </div>
      </div>

      {/* Live Extracted Emails Table */}
      <div className="glass-panel p-6 rounded-2xl border border-[#8a2be2]/25 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <PulseDot color="green" />
            <h3 className="text-base font-bold text-white tracking-wide">
              Live Harvested Contacts (Real-Time Feed)
            </h3>
          </div>
          <span className="text-xs font-mono text-[#8a8aa0]">
            Displaying latest {recentEmails.length} entries
          </span>
        </div>

        <div className="overflow-x-auto rounded-xl border border-[#8a2be2]/20">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-[#050508]/70 text-[#8a8aa0] border-b border-[#8a2be2]/25">
              <tr>
                <th className="p-3.5 tracking-wider">EMAIL ADDRESS</th>
                <th className="p-3.5 tracking-wider">CATEGORY</th>
                <th className="p-3.5 tracking-wider">TARGET SOURCE</th>
                <th className="p-3.5 tracking-wider text-right">TIMESTAMP</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#8a2be2]/10 bg-[#0c0816]/40">
              {recentEmails.length === 0 ? (
                <tr>
                  <td colSpan={4} className="p-8 text-center text-[#6a6a80]">
                    No contacts recorded yet. Start single or infinite crawler session to begin harvesting.
                  </td>
                </tr>
              ) : (
                recentEmails.map((item, idx) => {
                  const isPersonal = ['gmail.com', 'yandex.ru', 'mail.ru', 'yahoo.com', 'proton.me', 'outlook.com'].some(
                    d => item.email.includes(d)
                  );
                  return (
                    <tr key={idx} className="hover:bg-[#8a2be2]/10 transition-colors">
                      <td className="p-3.5 text-[#00f3ff] font-semibold flex items-center gap-2">
                        <span>{item.email}</span>
                      </td>
                      <td className="p-3.5">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider ${
                            isPersonal
                              ? 'bg-[#00ff9d]/15 text-[#00ff9d] border border-[#00ff9d]/30'
                              : 'bg-[#8a2be2]/20 text-[#c084fc] border border-[#8a2be2]/30'
                          }`}
                        >
                          {isPersonal ? 'HUMAN / PERSONAL' : 'CORPORATE / DEV'}
                        </span>
                      </td>
                      <td className="p-3.5 text-[#b026ff] truncate max-w-xs">
                        <span className="flex items-center gap-1">
                          <ArrowUpRight className="w-3 h-3 shrink-0" />
                          <span className="truncate">{item.source || 'Direct Harvest'}</span>
                        </span>
                      </td>
                      <td className="p-3.5 text-right text-[#6a6a80]">{item.time}</td>
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
