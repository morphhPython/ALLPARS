import React, { useState } from 'react';
import { BarChart3, Download, Copy, Check, Plus, Database, FileSpreadsheet, HardDrive } from 'lucide-react';
import { RainbowLine } from './RainbowLine';

interface StatsPageProps {
  totalEmails: number;
  personalEmails: number;
  allEmails: string[];
  personalList: string[];
  filePath: string;
  personalFilePath: string;
  onAddManualEmails: (emails: string[]) => Promise<void>;
}

export const StatsPage: React.FC<StatsPageProps> = ({
  totalEmails,
  personalEmails,
  allEmails,
  personalList,
  filePath,
  personalFilePath,
  onAddManualEmails,
}) => {
  const [manualInput, setManualInput] = useState<string>('');
  const [copiedType, setCopiedType] = useState<string | null>(null);
  const [isAdding, setIsAdding] = useState<boolean>(false);
  const [addMsg, setAddMsg] = useState<string | null>(null);

  const handleCopy = (text: string, type: string) => {
    navigator.clipboard.writeText(text);
    setCopiedType(type);
    setTimeout(() => setCopiedType(null), 1500);
  };

  const handleDownload = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualInput.trim()) return;
    setIsAdding(true);
    setAddMsg(null);
    try {
      const extracted = manualInput
        .split(/[\n,;\s]+/)
        .map(e => e.trim().toLowerCase())
        .filter(e => e.includes('@'));

      await onAddManualEmails(extracted);
      setManualInput('');
      setAddMsg(`Successfully merged ${extracted.length} emails into storage.`);
    } catch (err: any) {
      setAddMsg(`Error: ${err.message}`);
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-extrabold text-white tracking-wider flex items-center gap-3">
              <BarChart3 className="w-7 h-7 text-[#00f3ff]" />
              <span>Database Storage & Analytics</span>
            </h2>
            <p className="text-xs text-[#8a8aa0] mt-1 font-mono">
              Persistent local TXT files, verified human mailboxes, and manual list ingestion
            </p>
          </div>
        </div>
        <RainbowLine className="mt-4" />
      </div>

      {/* Two Big Hero Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel p-8 rounded-3xl border border-[#00f3ff]/30 space-y-4 relative overflow-hidden group">
          <div className="flex items-center justify-between text-[#8a8aa0] font-mono text-xs uppercase">
            <span>Total Harvested Records (BazaPochtRassilka.txt)</span>
            <Database className="w-5 h-5 text-[#00f3ff]" />
          </div>
          <div className="text-6xl font-black text-[#00f3ff] font-mono tracking-tight drop-shadow-[0_0_20px_rgba(0,243,255,0.4)]">
            {totalEmails}
          </div>
          <p className="text-xs font-mono text-[#6a6a80]">
            Complete harvested database including public repositories, forums, and developer directories.
          </p>

          <div className="flex gap-3 pt-3 border-t border-[#8a2be2]/20">
            <button
              onClick={() => handleDownload(allEmails.join('\n'), 'BazaPochtRassilka.txt')}
              className="flex-1 py-2.5 rounded-xl bg-[#00f3ff]/15 hover:bg-[#00f3ff]/25 text-[#00f3ff] border border-[#00f3ff]/40 font-mono text-xs font-bold flex items-center justify-center gap-2"
            >
              <Download className="w-4 h-4" />
              <span>Download TXT</span>
            </button>
            <button
              onClick={() => handleCopy(allEmails.join('\n'), 'all')}
              className="px-4 py-2.5 rounded-xl bg-[#8a2be2]/20 hover:bg-[#8a2be2]/30 text-[#c084fc] font-mono text-xs font-bold flex items-center gap-2"
            >
              {copiedType === 'all' ? <Check className="w-4 h-4 text-[#00ff9d]" /> : <Copy className="w-4 h-4" />}
              <span>Copy</span>
            </button>
          </div>

          <div className="text-[10px] font-mono text-[#4a4a5a] truncate">
            Target File: {filePath}
          </div>
        </div>

        <div className="glass-panel p-8 rounded-3xl border border-[#00ff9d]/30 space-y-4 relative overflow-hidden group">
          <div className="flex items-center justify-between text-[#8a8aa0] font-mono text-xs uppercase">
            <span>Personal Human Mailboxes (BazaPochtLichnie.txt)</span>
            <HardDrive className="w-5 h-5 text-[#00ff9d]" />
          </div>
          <div className="text-6xl font-black text-[#00ff9d] font-mono tracking-tight drop-shadow-[0_0_20px_rgba(0,255,157,0.4)]">
            {personalEmails}
          </div>
          <p className="text-xs font-mono text-[#6a6a80]">
            Verified human boxes on Gmail, Yandex, Mail.ru, Yahoo, Proton, Outlook. Free of bot/service accounts.
          </p>

          <div className="flex gap-3 pt-3 border-t border-[#8a2be2]/20">
            <button
              onClick={() => handleDownload(personalList.join('\n'), 'BazaPochtLichnie.txt')}
              className="flex-1 py-2.5 rounded-xl bg-[#00ff9d]/15 hover:bg-[#00ff9d]/25 text-[#00ff9d] border border-[#00ff9d]/40 font-mono text-xs font-bold flex items-center justify-center gap-2"
            >
              <Download className="w-4 h-4" />
              <span>Download Personal TXT</span>
            </button>
            <button
              onClick={() => handleCopy(personalList.join('\n'), 'personal')}
              className="px-4 py-2.5 rounded-xl bg-[#8a2be2]/20 hover:bg-[#8a2be2]/30 text-[#c084fc] font-mono text-xs font-bold flex items-center gap-2"
            >
              {copiedType === 'personal' ? <Check className="w-4 h-4 text-[#00ff9d]" /> : <Copy className="w-4 h-4" />}
              <span>Copy</span>
            </button>
          </div>

          <div className="text-[10px] font-mono text-[#4a4a5a] truncate">
            Target File: {personalFilePath}
          </div>
        </div>
      </div>

      {/* Manual Ingestion Box */}
      <div className="glass-panel p-6 rounded-2xl border border-[#8a2be2]/30 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Plus className="w-4 h-4 text-[#00f3ff]" />
            <h3 className="text-xs font-mono uppercase font-bold text-white tracking-wider">
              Manual Email Ingestion & Deduplication
            </h3>
          </div>
          <span className="text-[11px] font-mono text-[#8a8aa0]">
            Paste raw text, CSV, or line-separated list
          </span>
        </div>

        <form onSubmit={handleAddSubmit} className="space-y-3 font-mono text-xs">
          <textarea
            rows={5}
            value={manualInput}
            onChange={(e) => setManualInput(e.target.value)}
            placeholder="Paste emails separated by newlines, commas, or spaces (e.g. dev1@gmail.com, dev2@yandex.ru)..."
            className="w-full bg-[#050508] text-white p-3.5 rounded-xl border border-[#8a2be2]/35 focus:border-[#00f3ff] outline-none"
          />

          <div className="flex items-center justify-between">
            {addMsg ? (
              <span className="text-xs font-mono text-[#00ff9d]">{addMsg}</span>
            ) : <span />}

            <button
              type="submit"
              disabled={isAdding || !manualInput.trim()}
              className="px-6 py-2.5 rounded-xl bg-[#00f3ff]/20 hover:bg-[#00f3ff]/30 text-[#00f3ff] border border-[#00f3ff]/40 font-bold uppercase tracking-wider disabled:opacity-40"
            >
              {isAdding ? 'Merging...' : 'Ingest & Deduplicate'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
