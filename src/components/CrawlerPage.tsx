import React, { useState } from 'react';
import {
  Play,
  Infinity as InfinityIcon,
  Square,
  Terminal as TerminalIcon,
  Sparkles,
  Filter,
  Search,
  Globe,
  Send,
  ExternalLink,
  Plus,
  ArrowRight,
  ShieldCheck,
  Check,
} from 'lucide-react';
import { RainbowLine, PulseDot } from './RainbowLine';
import { CrawlerStatus } from '../types';

interface CrawlerPageProps {
  status: CrawlerStatus;
  onStartCrawler: (seeds: string[], infinite: boolean, maxPages: number, dorks?: string[], engine?: string) => void;
  onStopCrawler: () => void;
  onAddEmails: (emails: string[]) => void;
}

export const DORK_PRESETS = [
  {
    title: 'GitHub Maintainers (Personal Emails)',
    dork: 'site:github.com "gmail.com" inurl:MAINTAINERS',
    engine: 'duckduckgo',
    desc: 'Target public developer lists inside active git projects',
  },
  {
    title: 'Habr & RuNet Devs (Yandex / Mail.ru / Gmail)',
    dork: 'site:habr.com ("@yandex.ru" OR "@gmail.com" OR "@mail.ru")',
    engine: 'yandex',
    desc: 'Find author bios, open-source articles and discussions in Russian tech community',
  },
  {
    title: 'Public Mailmap / Contributor Dumps',
    dork: 'site:github.com inurl:.mailmap "gmail.com"',
    engine: 'google',
    desc: 'Extract full verified contributor address listings',
  },
  {
    title: 'Telegram Channel / Bio Contacts',
    dork: 'site:t.me "contact" ("@gmail.com" OR "@yandex.ru")',
    engine: 'bing',
    desc: 'Discover channel administrators and public outreach contacts',
  },
  {
    title: 'Open Contact Lists & Resumes',
    dork: 'filetype:txt "@gmail.com" "contacts" -sample',
    engine: 'duckduckgo',
    desc: 'Find plain text public files containing verified emails',
  },
];

export const CrawlerPage: React.FC<CrawlerPageProps> = ({
  status,
  onStartCrawler,
  onStopCrawler,
  onAddEmails,
}) => {
  // Seeds
  const [seedsText, setSeedsText] = useState<string>(`https://raw.githubusercontent.com/torvalds/linux/master/MAINTAINERS
https://raw.githubusercontent.com/git/git/master/.mailmap
https://raw.githubusercontent.com/golang/go/master/CONTRIBUTORS
https://raw.githubusercontent.com/rust-lang/rust/master/AUTHORS
https://raw.githubusercontent.com/nodejs/node/main/AUTHORS
https://news.ycombinator.com
https://lobste.rs`);

  const [maxPages, setMaxPages] = useState<number>(50);
  const [filterType, setFilterType] = useState<'all' | 'success' | 'warn' | 'err'>('all');

  // Integrated Dork Search Controls
  const [activeSubTab, setActiveSubTab] = useState<'spider' | 'dork'>('spider');
  const [dorkEngine, setDorkEngine] = useState<'duckduckgo' | 'google' | 'bing' | 'yandex'>('duckduckgo');
  const [dorkQuery, setDorkQuery] = useState<string>('site:github.com "gmail.com" inurl:MAINTAINERS');
  const [dorkLoading, setDorkLoading] = useState<boolean>(false);
  const [dorkResults, setDorkResults] = useState<{ links: string[]; emailsFound: string[] } | null>(null);
  const [dorkMsg, setDorkMsg] = useState<string | null>(null);
  const [autoDorkEnabled, setAutoDorkEnabled] = useState<boolean>(true);

  const handleStart = (infinite: boolean) => {
    const seeds = seedsText
      .split('\n')
      .map(s => s.trim())
      .filter(s => s.length > 0);

    const dorksToRun = autoDorkEnabled && dorkQuery.trim() ? [dorkQuery.trim()] : undefined;
    onStartCrawler(seeds, infinite, maxPages, dorksToRun, dorkEngine);
  };

  // Run dork directly inside the parser
  const handleExecuteDork = async () => {
    if (!dorkQuery.trim()) return;
    setDorkLoading(true);
    setDorkMsg(null);

    try {
      const res = await fetch('/api/dorks/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          engine: dorkEngine,
          query: dorkQuery.trim(),
          autoQueue: true,
        }),
      });

      const data = await res.json();
      if (res.ok) {
        setDorkResults({
          links: data.links || [],
          emailsFound: data.emailsFound || [],
        });
        if (data.emailsFound && data.emailsFound.length > 0) {
          onAddEmails(data.emailsFound);
        }
        setDorkMsg(`Найдено ${data.links?.length || 0} ссылок и ${data.emailsFound?.length || 0} почт. Ссылки автоматически добавлены в очередь паука!`);
      } else {
        setDorkMsg(`Ошибка: ${data.error || 'Сбой запроса'}`);
      }
    } catch (err: any) {
      setDorkMsg(`Ошибка сети: ${err.message}`);
    } finally {
      setDorkLoading(false);
    }
  };

  const filteredLogs = status.logs.filter(log => {
    if (filterType === 'all') return true;
    return log.type === filterType;
  });

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-extrabold text-white tracking-wider flex items-center gap-3">
              <TerminalIcon className="w-7 h-7 text-[#00f3ff]" />
              <span>Spider Crawler & Dork Parser</span>
            </h2>
            <p className="text-xs text-[#8a8aa0] mt-1 font-mono">
              Рекурсивный паук обхода ссылок со встроенным автоматическим Dork-поиском (Google, DuckDuckGo, Bing, Yandex)
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-mono px-3 py-1.5 rounded-lg bg-[#00f3ff]/10 text-[#00f3ff] border border-[#00f3ff]/30 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Dorks + Spider Unified</span>
            </span>
          </div>
        </div>
        <RainbowLine className="mt-4" />
      </div>

      {/* Mode Sub-Tabs (Unified Spider & Dorks) */}
      <div className="flex items-center gap-3 border-b border-[#8a2be2]/20 pb-3">
        <button
          onClick={() => setActiveSubTab('spider')}
          className={`px-4 py-2 rounded-xl text-xs font-mono font-bold uppercase tracking-wider transition-all flex items-center gap-2 ${
            activeSubTab === 'spider'
              ? 'bg-[#00f3ff]/20 text-[#00f3ff] border border-[#00f3ff]/40 shadow-[0_0_15px_rgba(0,243,255,0.2)]'
              : 'bg-[#050508] text-[#8a8aa0] hover:text-white'
          }`}
        >
          <TerminalIcon className="w-3.5 h-3.5" />
          <span>Spider Seeds & Queue</span>
        </button>

        <button
          onClick={() => setActiveSubTab('dork')}
          className={`px-4 py-2 rounded-xl text-xs font-mono font-bold uppercase tracking-wider transition-all flex items-center gap-2 ${
            activeSubTab === 'dork'
              ? 'bg-[#00ff9d]/20 text-[#00ff9d] border border-[#00ff9d]/40 shadow-[0_0_15px_rgba(0,255,157,0.2)]'
              : 'bg-[#050508] text-[#8a8aa0] hover:text-white'
          }`}
        >
          <Search className="w-3.5 h-3.5" />
          <span>Встроенный Dork Поиск (4 Движка)</span>
        </button>
      </div>

      {/* SUB-TAB 1: Spider Seeds & Recursive Settings */}
      {activeSubTab === 'spider' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          {/* Seeds Editor */}
          <div className="lg:col-span-2 glass-panel p-5 rounded-2xl border border-[#8a2be2]/30 space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-xs font-mono uppercase text-[#00f3ff] font-bold flex items-center gap-2">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Начальные ссылки / Репозитории (1 на строку)</span>
              </label>
              <span className="text-[11px] text-[#6a6a80] font-mono">
                Паук переходит по всем найденным ссылкам бесконечно
              </span>
            </div>

            <textarea
              rows={6}
              value={seedsText}
              onChange={(e) => setSeedsText(e.target.value)}
              disabled={status.running}
              className="w-full bg-[#050508]/80 text-[#00ff9d] font-mono text-xs p-3.5 rounded-xl border border-[#8a2be2]/30 focus:border-[#00f3ff] outline-none resize-none transition-colors"
              placeholder="Введите ссылки на страницы, файлы или репозитории..."
            />

            <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
              <div className="flex items-center gap-3">
                <label className="text-xs font-mono text-[#8a8aa0]">Лимит пачки:</label>
                <input
                  type="number"
                  min={10}
                  max={500}
                  value={maxPages}
                  onChange={(e) => setMaxPages(Number(e.target.value))}
                  disabled={status.running}
                  className="w-20 bg-[#050508] border border-[#8a2be2]/40 rounded-lg px-2.5 py-1 text-xs font-mono text-white text-center"
                />
                <span className="text-[11px] text-[#6a6a80] font-mono">страниц</span>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="autodork"
                  checked={autoDorkEnabled}
                  onChange={(e) => setAutoDorkEnabled(e.target.checked)}
                  className="accent-[#00f3ff]"
                />
                <label htmlFor="autodork" className="text-xs font-mono text-[#00f3ff] cursor-pointer">
                  Авто-подмешивать результаты Dork поиска
                </label>
              </div>
            </div>
          </div>

          {/* Action Matrix */}
          <div className="glass-panel p-5 rounded-2xl border border-[#8a2be2]/30 flex flex-col justify-between space-y-4">
            <div>
              <h3 className="text-xs font-mono uppercase text-[#b026ff] font-bold mb-3 flex items-center gap-2">
                <PulseDot color={status.running ? 'green' : 'purple'} active={status.running} />
                <span>Состояние Движка Паука</span>
              </h3>

              <div className="space-y-2.5 font-mono text-xs">
                <div className="flex justify-between py-1.5 border-b border-[#8a2be2]/15">
                  <span className="text-[#8a8aa0]">Статус:</span>
                  <span className={status.running ? 'text-[#00ff9d] font-bold' : 'text-[#6a6a80]'}>
                    {status.running ? (status.infinite ? 'БЕСКОНЕЧНЫЙ ОБХОД' : 'СЕССИЯ АКТИВНА') : 'ОСТАНОВЛЕН'}
                  </span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-[#8a2be2]/15">
                  <span className="text-[#8a8aa0]">Очередь ссылок:</span>
                  <span className="text-[#00f3ff] font-bold">{status.queueSize} ссылок</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-[#8a2be2]/15">
                  <span className="text-[#8a8aa0]">Посещено страниц:</span>
                  <span className="text-white font-bold">{status.pagesCrawled}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-[#8a2be2]/15">
                  <span className="text-[#8a8aa0]">Извлечено почт:</span>
                  <span className="text-[#00ff9d] font-bold">+{status.totalFound}</span>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              {!status.running ? (
                <>
                  <button
                    onClick={() => handleStart(false)}
                    className="w-full py-3 rounded-xl bg-[#00f3ff]/20 hover:bg-[#00f3ff]/30 text-[#00f3ff] border border-[#00f3ff]/50 text-xs font-bold font-mono uppercase tracking-wider flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(0,243,255,0.2)]"
                  >
                    <Play className="w-4 h-4" />
                    <span>Запустить Сессию (Парсер)</span>
                  </button>
                  <button
                    onClick={() => handleStart(true)}
                    className="w-full py-3 rounded-xl bg-[#00ff9d]/20 hover:bg-[#00ff9d]/30 text-[#00ff9d] border border-[#00ff9d]/50 text-xs font-bold font-mono uppercase tracking-wider flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(0,255,157,0.2)]"
                  >
                    <InfinityIcon className="w-4 h-4" />
                    <span>Бесконечный Паук (Crawler)</span>
                  </button>
                </>
              ) : (
                <button
                  onClick={onStopCrawler}
                  className="w-full py-3.5 rounded-xl bg-[#ff2a6d]/25 hover:bg-[#ff2a6d]/35 text-[#ff2a6d] border border-[#ff2a6d]/50 text-xs font-bold font-mono uppercase tracking-wider flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(255,42,109,0.3)] animate-pulse"
                >
                  <Square className="w-4 h-4" />
                  <span>Остановить Движок</span>
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* SUB-TAB 2: Integrated Dork Search Engine */}
      {activeSubTab === 'dork' && (
        <div className="space-y-5">
          {/* Engine Selector */}
          <div className="flex items-center gap-3">
            {(
              [
                { id: 'duckduckgo', name: 'DuckDuckGo', color: '#ffcc00' },
                { id: 'google', name: 'Google', color: '#00f3ff' },
                { id: 'bing', name: 'Bing', color: '#00ff9d' },
                { id: 'yandex', name: 'Yandex', color: '#ff2a6d' },
              ] as const
            ).map(item => (
              <button
                key={item.id}
                onClick={() => setDorkEngine(item.id)}
                className={`px-4 py-2 rounded-xl text-xs font-mono font-bold uppercase tracking-wider transition-all flex items-center gap-2 ${
                  dorkEngine === item.id
                    ? 'bg-[#8a2be2]/30 text-white border border-[#00f3ff] shadow-[0_0_15px_rgba(0,243,255,0.25)]'
                    : 'bg-[#050508]/80 text-[#8a8aa0] hover:text-white border border-[#8a2be2]/20'
                }`}
              >
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: item.color }}
                />
                <span>{item.name}</span>
              </button>
            ))}
          </div>

          {/* Dork Query Bar */}
          <div className="glass-panel p-5 rounded-2xl border border-[#8a2be2]/30 space-y-4">
            <label className="text-xs font-mono text-[#00f3ff] font-bold flex items-center gap-2 uppercase">
              <Globe className="w-3.5 h-3.5" />
              <span>Поисковый Dork Запрос [{dorkEngine.toUpperCase()}]</span>
            </label>

            <div className="flex gap-3">
              <input
                type="text"
                value={dorkQuery}
                onChange={(e) => setDorkQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleExecuteDork()}
                className="flex-1 bg-[#050508]/90 text-[#00ff9d] font-mono text-sm px-4 py-3 rounded-xl border border-[#8a2be2]/35 focus:border-[#00f3ff] outline-none"
                placeholder="e.g. site:github.com 'gmail.com' inurl:CONTRIBUTORS"
              />
              <button
                onClick={handleExecuteDork}
                disabled={dorkLoading}
                className="px-6 py-3 rounded-xl bg-gradient-to-r from-[#8a2be2] to-[#00f3ff] text-white text-xs font-mono font-bold uppercase tracking-wider flex items-center gap-2 hover:opacity-95 disabled:opacity-50 shadow-[0_0_20px_rgba(138,43,226,0.3)] shrink-0"
              >
                {dorkLoading ? <PulseDot color="cyan" /> : <Send className="w-4 h-4" />}
                <span>{dorkLoading ? 'Поиск...' : 'Искать & Добавить в Паук'}</span>
              </button>
            </div>

            {dorkMsg && (
              <div className="p-3 rounded-xl bg-[#050508] border border-[#00ff9d]/30 text-[#00ff9d] text-xs font-mono">
                {dorkMsg}
              </div>
            )}
          </div>

          {/* Preset Dorks */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
            {DORK_PRESETS.map((p, idx) => (
              <div
                key={idx}
                className="glass-panel p-4 rounded-xl border border-[#8a2be2]/20 hover:border-[#00f3ff]/40 transition-all flex flex-col justify-between space-y-3 group"
              >
                <div>
                  <div className="flex items-center justify-between text-xs font-bold text-white mb-1">
                    <span>{p.title}</span>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#8a2be2]/20 text-[#c084fc] uppercase">
                      {p.engine}
                    </span>
                  </div>
                  <p className="text-[11px] text-[#8a8aa0]">{p.desc}</p>
                </div>

                <div className="space-y-2 pt-1 border-t border-[#8a2be2]/15">
                  <code className="text-[11px] text-[#00f3ff] font-mono block truncate bg-[#050508]/80 p-1.5 rounded border border-[#8a2be2]/20">
                    {p.dork}
                  </code>
                  <button
                    onClick={() => {
                      setDorkQuery(p.dork);
                      setDorkEngine(p.engine as any);
                    }}
                    className="w-full py-1.5 rounded-lg bg-[#00f3ff]/10 hover:bg-[#00f3ff]/20 text-[#00f3ff] text-[11px] font-mono font-semibold flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <span>Выбрать шаблон</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Dork Results Feed */}
          {dorkResults && (
            <div className="glass-panel p-5 rounded-2xl border border-[#8a2be2]/30 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-[#00ff9d]">
                  Найдено результатов: {dorkResults.links.length} ссылок, {dorkResults.emailsFound.length} прямых почт
                </span>
              </div>

              {dorkResults.emailsFound.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {dorkResults.emailsFound.map((em, i) => (
                    <span key={i} className="text-xs font-mono px-2 py-0.5 rounded bg-[#050508] text-[#00f3ff] border border-[#8a2be2]/30">
                      {em}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Real-time Terminal Log Feed */}
      <div className="glass-panel p-5 rounded-2xl border border-[#8a2be2]/30 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <TerminalIcon className="w-4 h-4 text-[#00ff9d]" />
            <span className="text-xs font-mono uppercase font-bold text-white tracking-wider">
              ТЕРМИНАЛ ОБХОДА ПАУКА & ДОРКОВ // LIVE LOG STREAM
            </span>
          </div>

          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-[#6a6a80]" />
            {(['all', 'success', 'warn', 'err'] as const).map(type => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={`px-2.5 py-1 rounded text-[10px] font-mono uppercase tracking-wider ${
                  filterType === type
                    ? 'bg-[#00f3ff]/20 text-[#00f3ff] border border-[#00f3ff]/40'
                    : 'bg-[#050508]/60 text-[#6a6a80] hover:text-[#b0b0c0]'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        <div className="h-80 overflow-y-auto rounded-xl bg-[#050508]/90 border border-[#8a2be2]/25 p-4 font-mono text-xs space-y-1.5">
          {filteredLogs.length === 0 ? (
            <div className="text-[#6a6a80] text-center pt-24">
              Терминал готов к работе. Нажмите &quot;Запустить Сессию&quot; или выполните Dork поиск выше.
            </div>
          ) : (
            filteredLogs.map(log => {
              const colorClasses = {
                info: 'text-[#00f3ff]',
                success: 'text-[#00ff9d] bg-[#00ff9d]/10 px-2 py-0.5 rounded border border-[#00ff9d]/20',
                warn: 'text-[#ffcc00]',
                err: 'text-[#ff2a6d]',
              };
              return (
                <div key={log.id} className="leading-relaxed flex items-start gap-2">
                  <span className="text-[#6a6a80] shrink-0">[{log.time}]</span>
                  <span className={colorClasses[log.type]}>{log.message}</span>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
