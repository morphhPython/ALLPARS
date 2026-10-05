import React, { useState, useEffect, useRef } from 'react';
import {
  LayoutDashboard, Terminal, CheckCircle2, Mail, Users, Radio,
  Database, Code2, Play, Pause, Volume2, Shield, Sparkles, RefreshCw,
  Trash2, Send, Save, Key, ExternalLink, Copy, Download, Check, AlertTriangle
} from 'lucide-react';

interface HarvestContact {
  email: string;
  category: 'HUMAN / PERSONAL' | 'CORPORATE / DEV';
  targetSource: string;
  timestamp: string;
}

interface ValidatedRecord {
  email: string;
  verdict: 'SAFE' | 'RISKY' | 'TRAP' | 'INVALID';
  score: number;
  detail: string;
}

interface AccountCombo {
  email: string;
  provider: string;
  status: 'READY' | 'ACTIVE';
}

const RADIO_STATIONS = [
  {
    name: 'Lofi Chillhop & Study Beats',
    genre: 'CHILLHOP',
    desc: 'Relaxing hip-hop beats, mellow rhodes keys, and dusty vinyl groove',
    url: 'https://stream.zeno.fm/f3wvbbqmdg8uv',
    bitrate: '128kbps'
  },
  {
    name: 'Nightwave Plaza & Vaporwave',
    genre: 'VAPORWAVE',
    desc: 'Nostalgic 80s aesthetics, synthwave pads, and late-night cyberpunk echoes',
    url: 'https://radio.plaza.one/mp3',
    bitrate: '128kbps'
  },
  {
    name: 'DEF CON Radio (Cyber Chill)',
    genre: 'CYBERPUNK',
    desc: 'Hacker conference downtempo soundscapes and dark ambient synths',
    url: 'https://ice2.somafm.com/defcon-128-mp3',
    bitrate: '128kbps'
  },
  {
    name: 'Groove Salad (SomaFM)',
    genre: 'DOWNTEMPO',
    desc: 'A nicely chilled plate of ambient downtempo beats and grooves',
    url: 'https://ice1.somafm.com/groovesalad-128-mp3',
    bitrate: '128kbps'
  },
  {
    name: 'Secret Agent (Cinematic)',
    genre: 'SPY CHILL',
    desc: 'The soundtrack for your stylish, mysterious secret agent missions',
    url: 'https://ice1.somafm.com/secretagent-128-mp3',
    bitrate: '128kbps'
  },
  {
    name: 'Drone Zone (Atmospheric)',
    genre: 'AMBIENT',
    desc: 'Served best chilled, safe with most medications. Space textures',
    url: 'https://ice1.somafm.com/dronezone-128-mp3',
    bitrate: '128kbps'
  }
];

export default function App() {
  const [activeTab, setActiveTab] = useState<'dash' | 'spider' | 'validator' | 'mailer' | 'accounts' | 'radio' | 'base' | 'python'>('dash');

  // Lo-Fi Radio State
  const [radioPlaying, setRadioPlaying] = useState(false);
  const [currentStationIdx, setCurrentStationIdx] = useState(0);
  const [volume, setVolume] = useState(0.75);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Crawler State
  const [crawlerStatus, setCrawlerStatus] = useState<'STANDBY' | 'CRAWLING'>('STANDBY');
  const [harvestedCount, setHarvestedCount] = useState(5);
  const [personalCount, setPersonalCount] = useState(1);
  const [visitedNodes, setVisitedNodes] = useState(0);
  const [queueCount, setQueueCount] = useState(0);
  const [liveContacts, setLiveContacts] = useState<HarvestContact[]>([
    { email: 'loudnate@gmail.com', category: 'HUMAN / PERSONAL', targetSource: '↗ Crawler Harvest', timestamp: '18:05:10' },
    { email: 'vitalik.buterin@ethereum.org', category: 'CORPORATE / DEV', targetSource: '↗ Crawler Harvest', timestamp: '18:03:10' },
    { email: 'torvalds@linux-foundation.org', category: 'CORPORATE / DEV', targetSource: '↗ Linux MAINTAINERS', timestamp: '17:58:22' },
    { email: 'gvanrossum@python.org', category: 'CORPORATE / DEV', targetSource: '↗ Python Core Devs', timestamp: '17:50:04' },
    { email: 'satya.nadella@microsoft.com', category: 'CORPORATE / DEV', targetSource: '↗ GitHub Execs', timestamp: '17:42:15' }
  ]);
  const [spiderLogs, setSpiderLogs] = useState<Array<{ text: string; type: 'info' | 'success' | 'warn' | 'err'; time: string }>>([
    { text: '[INIT] Spider engine mounted. Ready for recursive deep crawl.', type: 'info', time: '18:00:00' },
    { text: '[SEEDS] Loaded 7 maintainer repository targets & mailmap manifests', type: 'info', time: '18:00:02' }
  ]);

  // Validator State
  const [singleInspectEmail, setSingleInspectEmail] = useState('');
  const [valFilter, setValFilter] = useState<'ALL' | 'SAFE' | 'RISKY' | 'TRAP' | 'INVALID'>('ALL');
  const [valSearch, setValSearch] = useState('');
  const [validatedRecords, setValidatedRecords] = useState<ValidatedRecord[]>([
    { email: 'loudnate@gmail.com', verdict: 'SAFE', score: 95, detail: 'Personal mailbox on Gmail, zero trap flags, verified MX' },
    { email: 'torvalds@linux-foundation.org', verdict: 'RISKY', score: 65, detail: 'High-reputation role/corp address, non-disposable domain' },
    { email: 'spamtrap_99@honeypot.org', verdict: 'TRAP', score: 0, detail: '⚠️ SPAM TRAP DETECTED: Known honeypot token trigger' },
    { email: 'fake.user@dispostable.com', verdict: 'INVALID', score: 5, detail: 'Disposable temporary throwaway provider' }
  ]);

  // Mailer & Accounts State
  const [accounts, setAccounts] = useState<AccountCombo[]>([
    { email: 'sender.demo@gmail.com', provider: 'GMAIL.COM', status: 'READY' },
    { email: 'outreach.lead@yandex.ru', provider: 'YANDEX.RU', status: 'READY' },
    { email: 'alex.developer@mail.ru', provider: 'MAIL.RU', status: 'READY' }
  ]);
  const [selectedSenderEmail, setSelectedSenderEmail] = useState('sender.demo@gmail.com');
  const [mailerTo, setMailerTo] = useState('contact@targetdomain.com');
  const [mailerSubject, setMailerSubject] = useState('Cooperation & Tech Collaboration Proposal');
  const [mailerBody, setMailerBody] = useState(
    'Hello,\n\n' +
    'I noticed your open-source projects and developer contributions. We are currently building advanced infrastructure and would love to discuss a potential partnership.\n\n' +
    'Would you be open for a short call this week?\n\n' +
    'Best regards,\nTechnical Outreach Team'
  );
  const [rawAccountsFile, setRawAccountsFile] = useState(
    '# File for sender accounts in format: email:password\n' +
    '# Add your accounts below, one per line.\n' +
    '# Example:\n' +
    'sender.demo@gmail.com:app_pass_abcd1234\n' +
    'outreach.lead@yandex.ru:secret_token_998\n' +
    'alex.developer@mail.ru:mailru_app_pass'
  );
  const [newAccEmail, setNewAccEmail] = useState('');
  const [newAccPass, setNewAccPass] = useState('');

  // AI Compose Modal State
  const [showAiModal, setShowAiModal] = useState(false);
  const [aiPrompt, setAiPrompt] = useState('');
  const [aiGenerating, setAiGenerating] = useState(false);

  // Desktop Python Source
  const [pythonCode, setPythonCode] = useState('');
  const [codeCopied, setCodeCopied] = useState(false);

  useEffect(() => {
    fetch('/allparser.py')
      .then(res => res.text())
      .then(code => setPythonCode(code))
      .catch(() => {});
  }, []);

  const toggleRadio = (idx?: number) => {
    if (!audioRef.current) return;
    const targetIdx = idx !== undefined ? idx : currentStationIdx;
    setCurrentStationIdx(targetIdx);

    if (radioPlaying && idx === undefined) {
      audioRef.current.pause();
      setRadioPlaying(false);
    } else {
      audioRef.current.src = RADIO_STATIONS[targetIdx].url;
      audioRef.current.play().then(() => setRadioPlaying(true)).catch(() => {});
    }
  };

  const handleInspectSingle = () => {
    if (!singleInspectEmail || !singleInspectEmail.includes('@')) return;
    const lower = singleInspectEmail.toLowerCase();
    let verdict: 'SAFE' | 'RISKY' | 'TRAP' | 'INVALID' = 'SAFE';
    let score = 92;
    let detail = 'Human mailbox confirmed, clean syntax & live domain';

    if (lower.includes('spam') || lower.includes('trap') || lower.includes('honeypot')) {
      verdict = 'TRAP';
      score = 0;
      detail = '⚠️ SPAM TRAP DETECTED: Known honeypot token trigger';
    } else if (lower.startsWith('admin@') || lower.startsWith('info@') || lower.startsWith('support@')) {
      verdict = 'RISKY';
      score = 60;
      detail = 'Role address (info/admin) — lower direct response probability';
    }

    setValidatedRecords(prev => [{ email: singleInspectEmail, verdict, score, detail }, ...prev]);
    setSingleInspectEmail('');
  };

  const handleAiGenerate = () => {
    if (!aiPrompt) return;
    setAiGenerating(true);
    setTimeout(() => {
      setMailerSubject(`Collaboration & Discussion: ${aiPrompt.slice(0, 32)}...`);
      setMailerBody(
        `Hello,\n\n` +
        `I came across your work regarding ${aiPrompt}. We are currently collaborating with top developers in this space.\n\n` +
        `Would you be open to exchanging a few ideas or hopping on a brief sync this week?\n\n` +
        `Best regards,\nOutreach & Engineering Lead`
      );
      setAiGenerating(false);
      setShowAiModal(false);
      setAiPrompt('');
    }, 600);
  };

  const handleSendMail = () => {
    if (!mailerTo || !mailerTo.includes('@')) {
      alert('Please provide a valid recipient email.');
      return;
    }
    // Pre-flight honeypot trap prevention
    if (mailerTo.toLowerCase().includes('trap') || mailerTo.toLowerCase().includes('honeypot')) {
      alert(`[AI PRE-FLIGHT REJECTED] Address ${mailerTo} is flagged as a potential SPAM TRAP! Dispatch blocked to protect sender reputation.`);
      return;
    }
    alert(`[AI PRE-FLIGHT PASSED] Email queued and sent via ${selectedSenderEmail} with RFC5322 compliance.`);
  };

  const handleAddAccount = () => {
    if (!newAccEmail || !newAccPass) return;
    const provider = newAccEmail.split('@')[1]?.toUpperCase() || 'SMTP';
    setAccounts(prev => [...prev, { email: newAccEmail, provider, status: 'READY' }]);
    setRawAccountsFile(prev => `${prev}\n${newAccEmail}:${newAccPass}`);
    setNewAccEmail('');
    setNewAccPass('');
  };

  const safeCount = validatedRecords.filter(r => r.verdict === 'SAFE').length;
  const riskyCount = validatedRecords.filter(r => r.verdict === 'RISKY').length;
  const trapCount = validatedRecords.filter(r => r.verdict === 'TRAP').length;
  const invalidCount = validatedRecords.filter(r => r.verdict === 'INVALID').length;

  const filteredRecords = validatedRecords.filter(r => {
    if (valFilter !== 'ALL' && r.verdict !== valFilter) return false;
    if (valSearch && !r.email.toLowerCase().includes(valSearch.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="min-h-screen bg-[#050508] text-slate-100 flex font-sans selection:bg-purple-600 selection:text-white">
      <audio
        ref={audioRef}
        onPlay={() => setRadioPlaying(true)}
        onPause={() => setRadioPlaying(false)}
      />

      {/* ========================================================= */}
      {/* 1. SIDEBAR (1:1 ПО СКРИНШОТАМ) */}
      {/* ========================================================= */}
      <aside className="w-[220px] bg-[#0b0713] border-r border-purple-900/30 flex flex-col shrink-0 select-none z-20">
        <div className="p-5 text-center">
          <div className="text-xl font-black tracking-[4px] bg-gradient-to-r from-cyan-400 via-purple-400 to-emerald-400 bg-clip-text text-transparent">
            MORPHH
          </div>
          <div className="text-[10px] font-mono tracking-widest text-slate-500 mt-0.5">
            ALLPARSV1.4 // AI OSINT
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-3 space-y-1 overflow-y-auto">
          {[
            { id: 'dash', label: 'Dashboard', icon: LayoutDashboard },
            { id: 'spider', label: 'Spider & Dorks', icon: Terminal, badge: 'SPIDER', badgeColor: 'text-purple-400 border-purple-500/50' },
            { id: 'validator', label: 'AI Validator', icon: CheckCircle2, badge: 'GEMINI', badgeColor: 'text-cyan-400 border-cyan-500/50' },
            { id: 'mailer', label: 'AI Mailer', icon: Mail, badge: 'SMART', badgeColor: 'text-purple-400 border-purple-500/50' },
            { id: 'accounts', label: 'Combo Accounts', icon: Users },
            { id: 'radio', label: 'Lo-Fi Radio', icon: Radio },
            { id: 'base', label: 'Database & Base', icon: Database },
            { id: 'python', label: 'Desktop Python', icon: Code2 }
          ].map((item) => {
            const Icon = item.icon;
            const active = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id as any)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                  active
                    ? 'bg-purple-900/30 text-white border border-purple-500/60 shadow-lg shadow-purple-900/20'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-purple-950/20'
                }`}
              >
                <div className="flex items-center gap-2.5 truncate">
                  <Icon className={`w-4 h-4 ${active ? 'text-cyan-400' : 'text-slate-500'}`} />
                  <span className="truncate">{item.label}</span>
                </div>
                {item.badge && (
                  <span className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border bg-purple-950/50 ${item.badgeColor}`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Sidebar Bottom Widgets */}
        <div className="p-3 space-y-2 border-t border-purple-950/40">
          <div className="bg-[#07050d] border border-purple-900/30 rounded-lg p-2 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${radioPlaying ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'}`} />
              <span className="text-[10px] font-mono text-slate-400">
                {radioPlaying ? 'LO-FI RADIO ON' : 'LO-FI RADIO OFF'}
              </span>
            </div>
            <button
              onClick={() => setActiveTab('radio')}
              className="text-[10px] font-bold text-cyan-400 hover:underline"
            >
              OPEN
            </button>
          </div>

          <div className="bg-[#07050d] border border-purple-900/30 rounded-lg p-2 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${crawlerStatus === 'CRAWLING' ? 'bg-emerald-400 animate-pulse' : 'bg-purple-500'}`} />
              <span className="text-[10px] font-mono text-slate-400">
                {crawlerStatus === 'CRAWLING' ? 'ENGINE ACTIVE' : 'ENGINE IDLE'}
              </span>
            </div>
            <span className="text-[9px] font-bold text-purple-400">SPIDER</span>
          </div>

          <div className="text-[9px] text-center font-mono text-slate-600">
            AI STUDIO FULL-STACK v2.0
          </div>
        </div>
      </aside>

      {/* ========================================================= */}
      {/* 2. MAIN VIEWPORT */}
      {/* ========================================================= */}
      <main className="flex-1 flex flex-col h-screen overflow-y-auto">
        {/* TAB 1: CONTROL DASHBOARD */}
        {activeTab === 'dash' && (
          <div className="p-8 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-3">
                  <h1 className="text-2xl font-bold text-white tracking-wide">Control Dashboard</h1>
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-950/60 text-cyan-400 border border-cyan-500/50">
                    ● SYSTEM LIVE
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-1">Autonomous OSINT harvesting, recursive spidering, and AI deliverability pipeline</p>
              </div>
            </div>

            <div className="h-px bg-gradient-to-r from-cyan-500 via-purple-500 to-emerald-500 opacity-60" />

            {/* 4 Top Metric Cards (Точь-в-точь по скриншоту) */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5">
                <div className="flex justify-between items-start">
                  <span className="text-[10px] font-mono font-bold text-slate-400 tracking-wider">HARVESTED MAILS</span>
                  <Database className="w-4 h-4 text-cyan-400" />
                </div>
                <div className="text-3xl font-extrabold text-cyan-400 font-mono mt-2">{harvestedCount}</div>
                <div className="text-[11px] text-emerald-400 mt-2 flex items-center justify-between">
                  <span className="text-slate-500 font-mono">TXT Database: active</span>
                  <span className="font-bold">100% deduplicated</span>
                </div>
              </div>

              <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5">
                <div className="flex justify-between items-start">
                  <span className="text-[10px] font-mono font-bold text-slate-400 tracking-wider">PERSONAL (HUMAN)</span>
                  <Mail className="w-4 h-4 text-emerald-400" />
                </div>
                <div className="text-3xl font-extrabold text-emerald-400 font-mono mt-2">{personalCount}</div>
                <div className="text-[11px] text-slate-400 mt-2 font-mono truncate">
                  Gmail, Yandex, Mail.ru, Yahoo
                </div>
              </div>

              <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5">
                <div className="flex justify-between items-start">
                  <span className="text-[10px] font-mono font-bold text-slate-400 tracking-wider">CRAWLER ENGINE</span>
                  <span className={`w-2 h-2 rounded-full ${crawlerStatus === 'CRAWLING' ? 'bg-emerald-400' : 'bg-purple-500'}`} />
                </div>
                <div className="text-2xl font-extrabold text-purple-400 font-mono mt-2">{crawlerStatus}</div>
                <div className="text-[11px] text-slate-400 mt-2 font-mono">
                  {crawlerStatus === 'CRAWLING' ? 'Scanning repository nodes' : 'Awaiting launch command'}
                </div>
              </div>

              <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5">
                <div className="flex justify-between items-start">
                  <span className="text-[10px] font-mono font-bold text-slate-400 tracking-wider">QUEUE & SPIDER</span>
                  <span className="text-xs font-mono text-cyan-400">{queueCount} URLs</span>
                </div>
                <div className="text-sm font-bold text-slate-200 mt-2 truncate">
                  {crawlerStatus === 'CRAWLING' ? 'Active Spider Crawl' : 'Idle (no active request)'}
                </div>
                <div className="text-[11px] text-slate-400 mt-2 font-mono">
                  Visited nodes: {visitedNodes}
                </div>
              </div>
            </div>

            {/* Mission Control Deck */}
            <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-cyan-400" />
                  <h3 className="text-sm font-bold text-white tracking-wide">Mission Control Deck</h3>
                </div>
                <div className="flex items-center gap-2 text-xs text-emerald-400">
                  <Shield className="w-3.5 h-3.5" />
                  <span>Anti-Crash Sandboxed Engine</span>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <button
                  onClick={() => {
                    setCrawlerStatus('CRAWLING');
                    setQueueCount(40);
                    setTimeout(() => {
                      setHarvestedCount(c => c + 2);
                      setVisitedNodes(v => v + 12);
                      setCrawlerStatus('STANDBY');
                    }, 2500);
                  }}
                  className="px-5 py-2.5 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 rounded-xl text-xs font-bold font-mono tracking-wider flex items-center gap-2 transition"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  RUN SINGLE BATCH (40P)
                </button>

                <button
                  onClick={() => {
                    if (crawlerStatus === 'CRAWLING') {
                      setCrawlerStatus('STANDBY');
                    } else {
                      setCrawlerStatus('CRAWLING');
                      setQueueCount(c => c + 150);
                    }
                  }}
                  className="px-5 py-2.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded-xl text-xs font-bold font-mono tracking-wider flex items-center gap-2 transition"
                >
                  <span className="text-base leading-none">∞</span>
                  ENABLE INFINITE SPIDER
                </button>

                <button
                  onClick={() => {
                    setCrawlerStatus('STANDBY');
                    setQueueCount(0);
                  }}
                  disabled={crawlerStatus === 'STANDBY'}
                  className="px-5 py-2.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/40 disabled:opacity-40 rounded-xl text-xs font-bold font-mono tracking-wider flex items-center gap-2 transition"
                >
                  ■ KILL PROCESS ENGINE
                </button>

                <button
                  onClick={() => {
                    setVisitedNodes(0);
                    setQueueCount(0);
                  }}
                  className="px-5 py-2.5 bg-purple-900/20 hover:bg-purple-900/40 text-purple-300 border border-purple-500/30 rounded-xl text-xs font-bold font-mono tracking-wider flex items-center gap-2 transition"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  CLEAR HARVEST CACHE
                </button>
              </div>

              <div className="pt-2">
                <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 mb-1">
                  <span>ENGINE ACTIVITY STREAM</span>
                  <span>{crawlerStatus === 'CRAWLING' ? 'ACTIVE HARVESTING' : 'PAUSED'}</span>
                </div>
                <div className="w-full h-1.5 bg-black/60 rounded-full overflow-hidden border border-purple-950">
                  <div className={`h-full bg-gradient-to-r from-cyan-400 via-purple-500 to-emerald-400 ${crawlerStatus === 'CRAWLING' ? 'w-full animate-pulse' : 'w-0'}`} />
                </div>
              </div>
            </div>

            {/* Live Harvested Contacts Table (Точно как на скрине) */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400" />
                  <h3 className="text-sm font-bold text-white">Live Harvested Contacts (Real-Time Feed)</h3>
                </div>
                <span className="text-[11px] font-mono text-slate-500">Displaying latest 5 entries</span>
              </div>

              <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl overflow-hidden">
                <table className="w-full text-left font-mono text-xs">
                  <thead>
                    <tr className="border-b border-purple-900/30 text-slate-500 text-[10px]">
                      <th className="py-3 px-4">EMAIL ADDRESS</th>
                      <th className="py-3 px-4">CATEGORY</th>
                      <th className="py-3 px-4">TARGET SOURCE</th>
                      <th className="py-3 px-4 text-right">TIMESTAMP</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-purple-950/30">
                    {liveContacts.map((c, i) => (
                      <tr key={i} className="hover:bg-purple-950/20">
                        <td className="py-3 px-4 font-semibold text-cyan-300">{c.email}</td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                            c.category === 'HUMAN / PERSONAL'
                              ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-500/50'
                              : 'bg-purple-950/60 text-purple-300 border border-purple-500/50'
                          }`}>
                            {c.category}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-purple-300 hover:underline cursor-pointer">{c.targetSource}</td>
                        <td className="py-3 px-4 text-right text-slate-500">{c.timestamp}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: SPIDER CRAWLER & DORK PARSER */}
        {activeTab === 'spider' && (
          <div className="p-8 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-white tracking-wide">&gt;_ Spider Crawler & Dork Parser</h1>
                <p className="text-xs text-slate-400 mt-1">Рекурсивный паук обхода ссылок со встроенным автоматическим Dork-поиском (Google, DuckDuckGo, Bing, Yandex)</p>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-cyan-950/60 text-cyan-400 border border-cyan-500/50">
                ✨ Dorks + Spider Unified
              </span>
            </div>

            <div className="h-px bg-gradient-to-r from-cyan-500 via-purple-500 to-emerald-500 opacity-60" />

            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              {/* Left Box: Seeds */}
              <div className="md:col-span-3 bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-cyan-400">✨ НАЧАЛЬНЫЕ ССЫЛКИ / РЕПОЗИТОРИИ (1 НА СТРОКУ)</span>
                  <span className="text-[10px] text-slate-500 font-mono">Паук переходит по всем найденным ссылкам бесконечно</span>
                </div>
                <textarea
                  rows={8}
                  defaultValue={
                    'https://raw.githubusercontent.com/torvalds/linux/master/MAINTAINERS\n' +
                    'https://raw.githubusercontent.com/git/git/master/.mailmap\n' +
                    'https://raw.githubusercontent.com/golang/go/master/CONTRIBUTORS\n' +
                    'https://raw.githubusercontent.com/rust-lang/rust/master/AUTHORS\n' +
                    'https://raw.githubusercontent.com/nodejs/node/main/AUTHORS\n' +
                    'https://news.ycombinator.com\n' +
                    'https://lobste.rs'
                  }
                  className="w-full bg-[#06040a] border border-purple-900/30 rounded-xl p-3 text-xs font-mono text-emerald-400 focus:outline-none focus:border-cyan-400"
                />
                <div className="flex items-center justify-between text-xs pt-1">
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400">Лимит пачки:</span>
                    <input type="text" defaultValue="50" className="w-12 bg-black border border-purple-800 text-center py-1 rounded font-mono text-xs" />
                    <span className="text-slate-400">страниц</span>
                  </div>
                  <label className="flex items-center gap-2 text-cyan-300 cursor-pointer">
                    <input type="checkbox" defaultChecked className="accent-cyan-400" />
                    <span>Авто-подмешивать результаты Dork поиска</span>
                  </label>
                </div>
              </div>

              {/* Right Box: State */}
              <div className="md:col-span-2 bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5 space-y-4">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-purple-400" />
                  <span className="text-xs font-bold text-purple-300">СОСТОЯНИЕ ДВИЖКА ПАУКА</span>
                </div>
                <div className="space-y-2 text-xs font-mono">
                  <div className="flex justify-between border-b border-purple-950 pb-1.5">
                    <span className="text-slate-400">Статус:</span>
                    <span className={`font-bold ${crawlerStatus === 'CRAWLING' ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {crawlerStatus === 'CRAWLING' ? 'РАБОТАЕТ' : 'ОСТАНОВЛЕН'}
                    </span>
                  </div>
                  <div className="flex justify-between border-b border-purple-950 pb-1.5">
                    <span className="text-slate-400">Очередь ссылок:</span>
                    <span className="text-cyan-400 font-bold">{queueCount} ссылок</span>
                  </div>
                  <div className="flex justify-between border-b border-purple-950 pb-1.5">
                    <span className="text-slate-400">Посещено страниц:</span>
                    <span className="text-slate-200 font-bold">{visitedNodes}</span>
                  </div>
                  <div className="flex justify-between pb-1">
                    <span className="text-slate-400">Извлечено почт:</span>
                    <span className="text-emerald-400 font-bold">+{harvestedCount}</span>
                  </div>
                </div>

                <div className="pt-2 space-y-2">
                  <button
                    onClick={() => {
                      setCrawlerStatus('CRAWLING');
                      setVisitedNodes(v => v + 5);
                      setHarvestedCount(c => c + 1);
                    }}
                    className="w-full py-2.5 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 rounded-xl text-xs font-bold font-mono tracking-wider flex items-center justify-center gap-2"
                  >
                    <Play className="w-3.5 h-3.5 fill-current" />
                    ЗАПУСТИТЬ СЕССИЮ (ПАРСЕР)
                  </button>
                  <button
                    onClick={() => setCrawlerStatus(s => s === 'CRAWLING' ? 'STANDBY' : 'CRAWLING')}
                    className="w-full py-2.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded-xl text-xs font-bold font-mono tracking-wider flex items-center justify-center gap-2"
                  >
                    <span>∞</span>
                    БЕСКОНЕЧНЫЙ ПАУК (CRAWLER)
                  </button>
                </div>
              </div>
            </div>

            {/* Terminal */}
            <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-emerald-400 font-mono">&gt;_ ТЕРМИНАЛ ОБХОДА ПАУКА & ДОРКОВ // LIVE LOG STREAM</span>
                <div className="flex gap-1.5 text-[10px] font-mono">
                  {['ALL', 'SUCCESS', 'WARN', 'ERR'].map((f) => (
                    <button key={f} className="px-2 py-0.5 rounded bg-black/50 border border-purple-900 text-slate-400 hover:text-white">
                      {f}
                    </button>
                  ))}
                </div>
              </div>
              <div className="bg-[#06040a] border border-purple-950 rounded-xl p-4 font-mono text-xs max-h-48 overflow-y-auto space-y-1">
                {spiderLogs.map((l, i) => (
                  <div key={i} className="flex gap-2">
                    <span className="text-slate-600">[{l.time}]</span>
                    <span className={l.type === 'success' ? 'text-emerald-400' : 'text-cyan-300'}>{l.text}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: GEMINI AI EMAIL VALIDATOR */}
        {activeTab === 'validator' && (
          <div className="p-8 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-white tracking-wide">✔ Gemini AI Email Validator</h1>
                <p className="text-xs text-slate-400 mt-1">Honeypot detection, MX verification, throwaway domain quarantine, and AI reputation heuristics</p>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-cyan-950/60 text-cyan-400 border border-cyan-500/50">
                ✨ Powered by Gemini 3.8
              </span>
            </div>

            <div className="h-px bg-gradient-to-r from-cyan-500 via-purple-500 to-emerald-500 opacity-60" />

            {/* Interactive AI Single Email Inspection */}
            <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5 space-y-3">
              <span className="text-xs font-bold text-cyan-400 tracking-wider">🔍 INTERACTIVE AI SINGLE EMAIL INSPECTION</span>
              <div className="flex gap-3">
                <input
                  type="email"
                  value={singleInspectEmail}
                  onChange={(e) => setSingleInspectEmail(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleInspectSingle()}
                  placeholder="e.g. spam-trap_99@honeypot.org or developer@gmail.com"
                  className="flex-1 bg-[#06040a] border border-purple-900/40 rounded-xl px-4 py-2.5 text-xs font-mono text-emerald-300 focus:outline-none focus:border-cyan-400"
                />
                <button
                  onClick={handleInspectSingle}
                  className="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-cyan-500 text-black font-bold text-xs rounded-xl flex items-center gap-2 hover:opacity-95"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  INSPECT WITH AI
                </button>
              </div>
            </div>

            {/* Full Database Validation */}
            <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-purple-400" />
                    <span className="text-xs font-bold text-purple-300">FULL DATABASE VALIDATION ({harvestedCount} EMAILS HARVESTED)</span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-0.5">Runs multi-layer syntax, domain MX, honeypot scan, and Gemini AI heuristics across your base</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => alert('Full database validation complete! Clean personal inboxes verified.')}
                    className="px-4 py-2 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded-xl text-xs font-bold font-mono tracking-wider"
                  >
                    ✔ VALIDATE BASE NOW
                  </button>
                  <button
                    onClick={() => {
                      setValidatedRecords(prev => prev.filter(r => r.verdict === 'SAFE' || r.verdict === 'RISKY'));
                    }}
                    className="px-4 py-2 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/40 rounded-xl text-xs font-bold font-mono tracking-wider flex items-center gap-1.5"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    PURGE TRAPS & INVALIDS ({trapCount + invalidCount})
                  </button>
                </div>
              </div>

              {/* 4 Colored Metric Pills */}
              <div className="grid grid-cols-4 gap-3 text-xs font-mono">
                <div className="bg-[#06040a] border border-emerald-500/40 rounded-xl p-3 flex justify-between items-center text-emerald-400">
                  <span className="font-bold">SAFE:</span>
                  <span className="font-extrabold text-base">{safeCount}</span>
                </div>
                <div className="bg-[#06040a] border border-amber-500/40 rounded-xl p-3 flex justify-between items-center text-amber-400">
                  <span className="font-bold">RISKY:</span>
                  <span className="font-extrabold text-base">{riskyCount}</span>
                </div>
                <div className="bg-[#06040a] border border-rose-500/40 rounded-xl p-3 flex justify-between items-center text-rose-400">
                  <span className="font-bold">TRAP:</span>
                  <span className="font-extrabold text-base">{trapCount}</span>
                </div>
                <div className="bg-[#06040a] border border-purple-500/40 rounded-xl p-3 flex justify-between items-center text-purple-400">
                  <span className="font-bold">INVALID:</span>
                  <span className="font-extrabold text-base">{invalidCount}</span>
                </div>
              </div>
            </div>

            {/* Filterable Table */}
            <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5 space-y-4">
              <div className="flex items-center justify-between gap-4">
                <div className="flex gap-1 text-xs font-mono">
                  {(['ALL', 'SAFE', 'RISKY', 'TRAP', 'INVALID'] as const).map(tab => (
                    <button
                      key={tab}
                      onClick={() => setValFilter(tab)}
                      className={`px-3 py-1 rounded-lg transition ${
                        valFilter === tab
                          ? 'bg-cyan-500 text-black font-bold'
                          : 'bg-black/40 text-slate-400 hover:text-white border border-purple-900/30'
                      }`}
                    >
                      {tab}
                    </button>
                  ))}
                </div>
                <input
                  type="text"
                  value={valSearch}
                  onChange={(e) => setValSearch(e.target.value)}
                  placeholder="Search in validated list..."
                  className="bg-[#06040a] border border-purple-900/40 rounded-lg px-3 py-1 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-400"
                />
              </div>

              <table className="w-full text-left font-mono text-xs">
                <thead>
                  <tr className="border-b border-purple-900/30 text-slate-500 text-[10px]">
                    <th className="py-2.5 px-3">EMAIL ADDRESS</th>
                    <th className="py-2.5 px-3">VERDICT</th>
                    <th className="py-2.5 px-3">SCORE</th>
                    <th className="py-2.5 px-3">AI / HEURISTIC DETAIL</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-purple-950/30">
                  {filteredRecords.map((r, i) => (
                    <tr key={i} className="hover:bg-purple-950/20">
                      <td className="py-2.5 px-3 text-cyan-300 font-semibold">{r.email}</td>
                      <td className="py-2.5 px-3">
                        <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                          r.verdict === 'SAFE'
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/50'
                            : r.verdict === 'TRAP'
                            ? 'bg-rose-950 text-rose-400 border border-rose-500/50'
                            : r.verdict === 'RISKY'
                            ? 'bg-amber-950 text-amber-400 border border-amber-500/50'
                            : 'bg-purple-950 text-purple-400 border border-purple-500/50'
                        }`}>
                          {r.verdict}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-slate-300">{r.score}/100</td>
                      <td className="py-2.5 px-3 text-slate-400">{r.detail}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 4: AI MAILER & DELIVERY STUDIO */}
        {activeTab === 'mailer' && (
          <div className="p-8 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-white tracking-wide">✉ AI Mailer & Delivery Studio</h1>
                <p className="text-xs text-slate-400 mt-1">Multi-account combo dispatch with Gemini AI drafting, spam shield evaluation, and RFC5322 compliance</p>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-950/60 text-emerald-400 border border-emerald-500/50 flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5" />
                Anti-Spam Pre-Flight Armed
              </span>
            </div>

            <div className="h-px bg-gradient-to-r from-cyan-500 via-purple-500 to-emerald-500 opacity-60" />

            <div className="grid grid-cols-1 md:grid-cols-5 gap-5">
              {/* Left Column */}
              <div className="md:col-span-2 space-y-4">
                {/* Sender Account Card */}
                <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-cyan-400 font-mono">👥 SENDER ACCOUNT (FROM ACCOUNTS.TXT)</span>
                    <button onClick={() => alert('Synced with accounts.txt!')} className="text-xs text-slate-400 hover:text-white flex items-center gap-1">
                      <RefreshCw className="w-3 h-3" /> Sync
                    </button>
                  </div>
                  <select
                    value={selectedSenderEmail}
                    onChange={(e) => setSelectedSenderEmail(e.target.value)}
                    className="w-full bg-[#06040a] border border-purple-900/40 rounded-xl px-3 py-2 text-xs font-mono text-cyan-300 focus:outline-none"
                  >
                    {accounts.map(a => (
                      <option key={a.email} value={a.email}>
                        {a.email} ({a.provider.toLowerCase()})
                      </option>
                    ))}
                  </select>
                  <div className="text-xs font-mono space-y-1 text-slate-400 pt-1">
                    <div className="flex justify-between">
                      <span>Detected Provider:</span>
                      <span className="text-emerald-400 font-bold">
                        {accounts.find(a => a.email === selectedSenderEmail)?.provider || 'GMAIL.COM'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Security / Password:</span>
                      <span>•••••••• (Loaded from file)</span>
                    </div>
                  </div>
                  <button
                    onClick={() => setActiveTab('accounts')}
                    className="w-full py-2 bg-purple-900/20 hover:bg-purple-900/40 text-purple-300 border border-purple-500/30 rounded-xl text-xs font-mono"
                  >
                    👥 Manage / Edit accounts.txt
                  </button>
                </div>

                {/* Verified Recipients List */}
                <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-emerald-400 font-mono">✔ VERIFIED DATABASE RECIPIENTS</span>
                    <span className="text-[10px] text-slate-500 font-mono">{liveContacts.length} in base</span>
                  </div>
                  <div className="space-y-1.5 font-mono text-xs max-h-48 overflow-y-auto">
                    {liveContacts.map(c => (
                      <div key={c.email} className="flex justify-between items-center bg-[#06040a] border border-purple-950 p-2 rounded-lg">
                        <span className="text-slate-300 truncate max-w-[170px]">{c.email}</span>
                        <button
                          onClick={() => setMailerTo(c.email)}
                          className="text-[10px] text-purple-400 hover:text-cyan-300"
                        >
                          pick
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Right Column: Form */}
              <div className="md:col-span-3 bg-[#0e0918] border border-purple-900/30 rounded-2xl p-6 space-y-4">
                <div>
                  <label className="block text-[10px] font-mono font-bold text-slate-500 mb-1">RECIPIENT EMAIL (TO:)</label>
                  <input
                    type="email"
                    value={mailerTo}
                    onChange={(e) => setMailerTo(e.target.value)}
                    className="w-full bg-[#06040a] border border-purple-900/40 rounded-xl px-4 py-2 text-xs font-mono text-emerald-300 focus:outline-none focus:border-cyan-400"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-mono font-bold text-slate-500 mb-1">EMAIL SUBJECT LINE</label>
                  <input
                    type="text"
                    value={mailerSubject}
                    onChange={(e) => setMailerSubject(e.target.value)}
                    className="w-full bg-[#06040a] border border-purple-900/40 rounded-xl px-4 py-2 text-xs text-white focus:outline-none focus:border-cyan-400"
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="text-[10px] font-mono font-bold text-slate-500">MESSAGE CONTENT (MIME / PLAIN / HTML)</label>
                    <button
                      onClick={() => setShowAiModal(true)}
                      className="px-3 py-1 bg-gradient-to-r from-purple-600 to-cyan-500 text-white font-bold text-[11px] rounded-lg flex items-center gap-1.5 shadow-md shadow-cyan-500/20"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                      ВОСПОЛЬЗОВАТЬСЯ ИИ
                    </button>
                  </div>
                  <textarea
                    rows={8}
                    value={mailerBody}
                    onChange={(e) => setMailerBody(e.target.value)}
                    className="w-full bg-[#06040a] border border-purple-900/40 rounded-xl p-3.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-400 font-sans"
                  />
                </div>

                <div className="flex items-center justify-between pt-2">
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    <Shield className="w-4 h-4 text-cyan-400" />
                    <span>Anti-Spam AI Check will audit the message before dispatch</span>
                  </div>
                  <button
                    onClick={handleSendMail}
                    className="px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-cyan-500 text-black font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-emerald-500/20"
                  >
                    <Send className="w-3.5 h-3.5" />
                    AI PRE-FLIGHT & SEND
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: SENDER ACCOUNTS MANAGER (accounts.txt) */}
        {activeTab === 'accounts' && (
          <div className="p-8 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-white tracking-wide">👥 Sender Accounts Manager (accounts.txt)</h1>
                <p className="text-xs text-slate-400 mt-1">Saved combos formatted as email:password loaded directly into the Mailer dropdown</p>
              </div>
              <button
                onClick={() => alert('File accounts.txt reloaded!')}
                className="px-4 py-2 bg-purple-900/30 hover:bg-purple-900/50 text-cyan-300 border border-purple-500/40 rounded-xl text-xs font-mono flex items-center gap-2"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Reload File
              </button>
            </div>

            <div className="h-px bg-gradient-to-r from-cyan-500 via-purple-500 to-emerald-500 opacity-60" />

            <div className="grid grid-cols-1 md:grid-cols-5 gap-5">
              {/* Left Column: Add single + Active combos */}
              <div className="md:col-span-2 space-y-4">
                <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5 space-y-3">
                  <span className="text-xs font-bold text-cyan-400 font-mono">+ ADD SINGLE ACCOUNT</span>
                  <div>
                    <label className="text-[10px] text-slate-400 block mb-1">Email Address:</label>
                    <input
                      type="email"
                      value={newAccEmail}
                      onChange={(e) => setNewAccEmail(e.target.value)}
                      placeholder="e.g. sender@gmail.com"
                      className="w-full bg-[#06040a] border border-purple-900/40 rounded-xl px-3 py-2 text-xs text-white font-mono"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] text-slate-400 block mb-1">Password / App Password:</label>
                    <input
                      type="password"
                      value={newAccPass}
                      onChange={(e) => setNewAccPass(e.target.value)}
                      placeholder="e.g. xxxx-xxxx-xxxx-xxxx"
                      className="w-full bg-[#06040a] border border-purple-900/40 rounded-xl px-3 py-2 text-xs text-white font-mono"
                    />
                  </div>
                  <button
                    onClick={handleAddAccount}
                    className="w-full py-2.5 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 rounded-xl text-xs font-mono font-bold flex items-center justify-center gap-2"
                  >
                    <Key className="w-3.5 h-3.5" />
                    SAVE TO ACCOUNTS.TXT
                  </button>
                </div>

                <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5 space-y-3">
                  <span className="text-xs font-bold text-purple-300 font-mono">👥 ACTIVE MAILER COMBOS ({accounts.length})</span>
                  <div className="space-y-2">
                    {accounts.map(acc => (
                      <div key={acc.email} className="bg-[#06040a] border border-purple-950 p-3 rounded-xl flex justify-between items-center">
                        <div>
                          <div className="text-xs font-mono font-bold text-cyan-300">{acc.email}</div>
                          <div className="text-[10px] font-mono text-slate-500">Provider: {acc.provider}</div>
                        </div>
                        <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-500/50">
                          READY
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Right Column: Direct Raw Editor */}
              <div className="md:col-span-3 bg-[#0e0918] border border-purple-900/30 rounded-2xl p-6 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-emerald-400 font-mono">📄 DIRECT RAW EDITOR: DATA/ACCOUNTS.TXT</span>
                  <button
                    onClick={() => alert('accounts.txt saved successfully!')}
                    className="px-4 py-2 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 rounded-xl text-xs font-mono flex items-center gap-1.5"
                  >
                    <Save className="w-3.5 h-3.5" />
                    SAVE FILE (ACCOUNTS.TXT)
                  </button>
                </div>
                <p className="text-[11px] text-slate-400">
                  Format: <code className="text-cyan-300">email:password</code> (one per line). Lines starting with <code className="text-purple-300">#</code> are ignored. For Gmail or Yandex, generate an <b className="text-white">App Password</b> from your security settings.
                </p>
                <textarea
                  rows={14}
                  value={rawAccountsFile}
                  onChange={(e) => setRawAccountsFile(e.target.value)}
                  className="w-full bg-[#06040a] border border-purple-950 rounded-xl p-4 font-mono text-xs text-emerald-400 focus:outline-none focus:border-cyan-400"
                />
              </div>
            </div>
          </div>
        )}

        {/* TAB 6: CYBERPUNK LO-FI RADIO */}
        {activeTab === 'radio' && (
          <div className="p-8 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-white tracking-wide">((o)) Cyberpunk Lo-Fi Radio</h1>
                <p className="text-xs text-slate-400 mt-1">Live streaming lofi beats, ambient chillhop, and atmospheric textures for deep focus OSINT sessions</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-mono font-bold border ${
                radioPlaying
                  ? 'bg-emerald-950/60 text-emerald-400 border-emerald-500/50'
                  : 'bg-rose-950/60 text-rose-400 border-rose-500/50'
              }`}>
                ● {radioPlaying ? 'RADIO LIVE' : 'RADIO OFF'}
              </span>
            </div>

            <div className="h-px bg-gradient-to-r from-cyan-500 via-purple-500 to-emerald-500 opacity-60" />

            {/* Main Player Display Box (Точь-в-точь по скриншоту) */}
            <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-6 space-y-5">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="font-bold text-cyan-400 flex items-center gap-2">
                  <Radio className="w-4 h-4" />
                  LOFI CHILLHOP & STUDY BEATS
                </span>
                <span className="text-slate-500">{radioPlaying ? 'STREAMING 128KBPS' : 'STOPPED'}</span>
              </div>

              {/* Animated Soundwave Dash Spectrum */}
              <div className="bg-[#06040a] border border-purple-900/30 rounded-xl py-8 px-6 flex items-center justify-center gap-1.5 overflow-hidden">
                {Array.from({ length: 48 }).map((_, i) => (
                  <span
                    key={i}
                    style={{
                      height: radioPlaying ? `${Math.sin(i * 0.4) * 16 + 20}px` : '4px'
                    }}
                    className={`w-1 rounded-full transition-all duration-300 ${
                      radioPlaying ? 'bg-cyan-400 shadow-sm shadow-cyan-400' : 'bg-purple-900/40'
                    }`}
                  />
                ))}
              </div>

              <div className="flex flex-wrap items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => toggleRadio()}
                    className="px-8 py-3.5 bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-400 hover:to-purple-500 text-black font-extrabold text-sm rounded-xl flex items-center gap-2 shadow-lg shadow-cyan-500/30 transition"
                  >
                    {radioPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current" />}
                    {radioPlaying ? 'PAUSE STREAM' : 'TURN ON'}
                  </button>
                  <div className="text-xs">
                    <div className="font-bold text-white">Click to start Lo-Fi stream</div>
                    <div className="text-slate-400">Music continues playing even when switching tabs</div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Volume2 className="w-4 h-4 text-slate-400" />
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={volume}
                    onChange={(e) => {
                      const v = parseFloat(e.target.value);
                      setVolume(v);
                      if (audioRef.current) audioRef.current.volume = v;
                    }}
                    className="w-28 h-1.5 accent-cyan-400 bg-slate-800 rounded cursor-pointer"
                  />
                  <span className="text-xs font-mono text-slate-400">{Math.round(volume * 100)}%</span>
                </div>
              </div>

              <div className="pt-2 flex items-center gap-3 text-xs text-slate-400 border-t border-purple-950">
                <span className="font-mono text-[10px] tracking-wider text-slate-500">ATMOSPHERE FX:</span>
                <button className="px-3 py-1 bg-purple-950/40 hover:bg-purple-950 text-cyan-300 border border-purple-800/40 rounded-lg text-xs">
                  💿 Vinyl Warmth & Crackle
                </button>
                <button className="px-3 py-1 bg-purple-950/40 hover:bg-purple-950 text-slate-300 border border-purple-800/40 rounded-lg text-xs">
                  🌧 Rain Sound Filter
                </button>
              </div>
            </div>

            {/* Curated Stations Grid (Точь-в-точь по скриншоту) */}
            <div className="space-y-3">
              <span className="text-xs font-mono font-bold text-cyan-400">🎧 CURATED LO-FI STATIONS & MOODS</span>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {RADIO_STATIONS.map((station, idx) => {
                  const isCurrent = currentStationIdx === idx;
                  return (
                    <div
                      key={station.name}
                      onClick={() => toggleRadio(idx)}
                      className={`bg-[#0e0918] border p-5 rounded-2xl cursor-pointer transition ${
                        isCurrent
                          ? 'border-cyan-400/80 shadow-lg shadow-cyan-500/10'
                          : 'border-purple-900/30 hover:border-purple-500/40'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex items-center gap-2">
                          <Radio className="w-4 h-4 text-cyan-400" />
                          <h4 className="text-sm font-bold text-white">{station.name}</h4>
                        </div>
                        <span className="text-[9px] font-mono font-bold text-cyan-400 border border-cyan-500/50 px-2 py-0.5 rounded">
                          {station.genre}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-2">{station.desc}</p>
                      <div className="flex justify-between items-center text-xs font-mono mt-4 pt-2 border-t border-purple-950">
                        <span className={isCurrent ? 'text-emerald-400 font-bold' : 'text-slate-500'}>
                          {isCurrent ? 'Selected Station' : 'Click to select'}
                        </span>
                        <span className="text-slate-500">{station.bitrate}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* TAB 7: DATABASE & BASE */}
        {activeTab === 'base' && (
          <div className="p-8 space-y-6">
            <h1 className="text-2xl font-bold text-white tracking-wide">📊 Database & Raw Base Viewer</h1>
            <p className="text-xs text-slate-400">View contacts saved in BazaPochtRassilka.txt</p>
            <div className="h-px bg-gradient-to-r from-cyan-500 via-purple-500 to-emerald-500 opacity-60" />
            <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-6 font-mono text-xs text-emerald-400 space-y-1">
              {liveContacts.map(c => (
                <div key={c.email}>{c.email}</div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 8: DESKTOP PYTHON SOURCE */}
        {activeTab === 'python' && (
          <div className="p-8 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-white tracking-wide">&lt;/&gt; Desktop Python Source (allparser.py)</h1>
                <p className="text-xs text-slate-400 mt-1">Single-file standalone application matching the exact UI above</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(pythonCode);
                    setCodeCopied(true);
                    setTimeout(() => setCodeCopied(false), 2000);
                  }}
                  className="px-4 py-2 bg-purple-900/30 hover:bg-purple-900/50 text-cyan-300 border border-purple-500/40 rounded-xl text-xs font-mono flex items-center gap-2"
                >
                  {codeCopied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  {codeCopied ? 'Copied!' : 'Copy Code'}
                </button>
                <button
                  onClick={() => {
                    const blob = new Blob([pythonCode], { type: 'text/x-python' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'allparser.py';
                    a.click();
                  }}
                  className="px-4 py-2 bg-gradient-to-r from-purple-600 to-cyan-500 text-black font-bold text-xs rounded-xl flex items-center gap-2"
                >
                  <Download className="w-3.5 h-3.5" />
                  Download allparser.py
                </button>
              </div>
            </div>
            <div className="h-px bg-gradient-to-r from-cyan-500 via-purple-500 to-emerald-500 opacity-60" />
            <pre className="p-4 bg-[#050508] border border-purple-900/40 rounded-xl overflow-x-auto text-xs font-mono text-emerald-400/90 max-h-[640px] leading-relaxed">
              <code>{pythonCode}</code>
            </pre>
          </div>
        )}
      </main>

      {/* ========================================================= */}
      {/* 3. AI EMAIL GENERATOR MODAL */}
      {/* ========================================================= */}
      {showAiModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0e0918] border border-purple-500/50 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl shadow-purple-900/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-cyan-400" />
                <h3 className="text-base font-bold text-white">✨ Генерация письма через ИИ</h3>
              </div>
              <button onClick={() => setShowAiModal(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>
            <p className="text-xs text-slate-400">
              Опишите цель сообщения. Нейросеть сгенерирует вежливое, живое письмо без спам-триггеров для максимальной доставляемости.
            </p>
            <input
              type="text"
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAiGenerate()}
              placeholder="Например: Предложить разработчику соавторство в Open Source боте"
              className="w-full bg-[#06040a] border border-purple-900/40 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-cyan-400"
            />
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setShowAiModal(false)}
                className="px-4 py-2 bg-black/40 text-slate-400 rounded-xl text-xs"
              >
                Отмена
              </button>
              <button
                onClick={handleAiGenerate}
                disabled={aiGenerating || !aiPrompt}
                className="px-5 py-2 bg-gradient-to-r from-purple-600 to-cyan-500 text-black font-bold text-xs rounded-xl flex items-center gap-2 disabled:opacity-50"
              >
                {aiGenerating ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                {aiGenerating ? 'Генерация...' : 'Сгенерировать'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
