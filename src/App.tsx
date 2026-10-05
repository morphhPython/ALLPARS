import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Sidebar, TabKey } from './components/Sidebar';
import { Dashboard } from './components/Dashboard';
import { CrawlerPage } from './components/CrawlerPage';
import { ValidatorPage } from './components/ValidatorPage';
import { MailerPage } from './components/MailerPage';
import { AccountsPage } from './components/AccountsPage';
import { LofiRadioPage, STATIONS } from './components/LofiRadioPage';
import { StatsPage } from './components/StatsPage';
import { PythonScriptPage } from './components/PythonScriptPage';
import { CyberBackground } from './components/CyberBackground';
import { EmailAccount, CrawlerStatus, ValidationItem } from './types';

export default function App() {
  const [currentTab, setCurrentTab] = useState<TabKey>('dashboard');

  // Crawler Status State
  const [crawlerStatus, setCrawlerStatus] = useState<CrawlerStatus>({
    running: false,
    infinite: false,
    pagesCrawled: 0,
    totalFound: 0,
    personalFound: 0,
    queueSize: 0,
    currentTarget: 'IDLE',
    visitedCount: 0,
    logs: [],
  });

  // Database Emails
  const [generalEmails, setGeneralEmails] = useState<string[]>([]);
  const [personalEmails, setPersonalEmails] = useState<string[]>([]);
  const [filePath, setFilePath] = useState<string>('BazaPochtRassilka.txt');
  const [personalFilePath, setPersonalFilePath] = useState<string>('BazaPochtLichnie.txt');

  // Accounts (email:password from accounts.txt)
  const [accounts, setAccounts] = useState<EmailAccount[]>([]);
  const [rawAccountsText, setRawAccountsText] = useState<string>('');

  // Validation State
  const [validationResults, setValidationResults] = useState<Record<string, ValidationItem>>({});
  const [isValidating, setIsValidating] = useState<boolean>(false);
  const [validationProgress, setValidationProgress] = useState<number>(0);

  // Recent feed for Dashboard
  const [recentFeed, setRecentFeed] = useState<{ email: string; source: string; time: string }[]>([]);

  // -------------------------------------------------------------
  // Persistent Lo-Fi Audio Radio Engine
  // -------------------------------------------------------------
  const [isRadioPlaying, setIsRadioPlaying] = useState<boolean>(false);
  const [radioVolume, setRadioVolume] = useState<number>(0.75);
  const [currentStationId, setCurrentStationId] = useState<string>(STATIONS[0].id);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const synthIntervalRef = useRef<any>(null);

  // Web Audio Synth ambient fallback if live stream has network error
  const startSynthAmbient = useCallback(() => {
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const chords = [
        [261.63, 329.63, 392.0, 493.88], // Cmaj7
        [220.0, 261.63, 329.63, 392.0],   // Am7
        [174.61, 220.0, 261.63, 329.63], // Fmaj7
        [196.0, 246.94, 293.66, 349.23], // G7
      ];
      let chordIndex = 0;

      const playChord = () => {
        if (!isRadioPlaying) return;
        const currentChord = chords[chordIndex % chords.length];
        chordIndex++;

        currentChord.forEach((freq, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          const filter = ctx.createBiquadFilter();

          filter.type = 'lowpass';
          filter.frequency.setValueAtTime(600, ctx.currentTime);

          osc.type = idx % 2 === 0 ? 'sine' : 'triangle';
          osc.frequency.setValueAtTime(freq, ctx.currentTime);

          gain.gain.setValueAtTime(0, ctx.currentTime);
          gain.gain.linearRampToValueAtTime(0.04 * radioVolume, ctx.currentTime + 1.5);
          gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 6.0);

          osc.connect(filter);
          filter.connect(gain);
          gain.connect(ctx.destination);

          osc.start(ctx.currentTime);
          osc.stop(ctx.currentTime + 6.5);
        });
      };

      playChord();
      synthIntervalRef.current = setInterval(playChord, 5500);
    } catch {
      // ignore
    }
  }, [isRadioPlaying, radioVolume]);

  const stopSynthAmbient = () => {
    if (synthIntervalRef.current) {
      clearInterval(synthIntervalRef.current);
      synthIntervalRef.current = null;
    }
  };

  const toggleRadio = () => {
    if (isRadioPlaying) {
      // Stop
      if (audioRef.current) {
        audioRef.current.pause();
      }
      stopSynthAmbient();
      setIsRadioPlaying(false);
    } else {
      // Start
      const station = STATIONS.find(s => s.id === currentStationId) || STATIONS[0];
      if (audioRef.current) {
        audioRef.current.src = station.url;
        audioRef.current.volume = radioVolume;
        const playPromise = audioRef.current.play();
        if (playPromise !== undefined) {
          playPromise
            .then(() => {
              setIsRadioPlaying(true);
            })
            .catch(() => {
              // Fallback to ambient chord synth
              setIsRadioPlaying(true);
              startSynthAmbient();
            });
        }
      }
    }
  };

  const handleStationChange = (stationId: string) => {
    setCurrentStationId(stationId);
    const station = STATIONS.find(s => s.id === stationId);
    if (!station) return;

    if (isRadioPlaying && audioRef.current) {
      stopSynthAmbient();
      audioRef.current.src = station.url;
      audioRef.current.volume = radioVolume;
      audioRef.current.play().catch(() => {
        startSynthAmbient();
      });
    }
  };

  const handleVolumeChange = (vol: number) => {
    setRadioVolume(vol);
    if (audioRef.current) {
      audioRef.current.volume = vol;
    }
  };

  // -------------------------------------------------------------
  // Data Fetching
  // -------------------------------------------------------------
  const fetchEmails = useCallback(async () => {
    try {
      const res = await fetch('/api/emails');
      if (res.ok) {
        const data = await res.json();
        setGeneralEmails(data.general || []);
        setPersonalEmails(data.personal || []);
        if (data.filePath) setFilePath(data.filePath);
        if (data.personalFilePath) setPersonalFilePath(data.personalFilePath);
      }
    } catch {
      // ignore network glitch
    }
  }, []);

  const fetchAccounts = useCallback(async () => {
    try {
      const res = await fetch('/api/accounts');
      if (res.ok) {
        const data = await res.json();
        setAccounts(data.accounts || []);
        setRawAccountsText(data.raw || '');
      }
    } catch {
      // ignore network glitch
    }
  }, []);

  const fetchCrawlerStatus = useCallback(async () => {
    try {
      const res = await fetch('/api/crawler/status');
      if (res.ok) {
        const data = await res.json();
        setCrawlerStatus(data);

        if (data.logs && data.logs.length > 0) {
          const successLogs = data.logs.filter((l: any) => l.type === 'success' && l.message.includes('Found +'));
          if (successLogs.length > 0) {
            fetchEmails();
          }
        }
      }
    } catch {
      // ignore network glitch
    }
  }, [fetchEmails]);

  useEffect(() => {
    fetchEmails();
    fetchAccounts();
    fetchCrawlerStatus();

    const interval = setInterval(() => {
      fetchCrawlerStatus();
    }, 1500);

    return () => clearInterval(interval);
  }, [fetchCrawlerStatus, fetchEmails, fetchAccounts]);

  useEffect(() => {
    if (generalEmails.length > 0) {
      const feed = generalEmails.slice(-15).reverse().map((em, idx) => ({
        email: em,
        source: 'Crawler Harvest',
        time: new Date(Date.now() - idx * 120000).toTimeString().split(' ')[0],
      }));
      setRecentFeed(feed);
    }
  }, [generalEmails]);

  // Crawler Controls
  const handleStartCrawler = async (seeds?: string[], infinite = false, maxPages = 40, dorks?: string[], engine?: string) => {
    try {
      await fetch('/api/crawler/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seeds, infinite, maxPages, dorks, dorkEngine: engine }),
      });
      fetchCrawlerStatus();
    } catch (err: any) {
      console.error('Failed to start crawler:', err);
    }
  };

  const handleStopCrawler = async () => {
    try {
      await fetch('/api/crawler/stop', { method: 'POST' });
      fetchCrawlerStatus();
    } catch (err: any) {
      console.error('Failed to stop crawler:', err);
    }
  };

  const handleClearDatabase = async () => {
    if (window.confirm('Очистить файлы базы BazaPochtRassilka.txt и BazaPochtLichnie.txt?')) {
      try {
        await fetch('/api/emails/clear', { method: 'POST' });
        fetchEmails();
        setValidationResults({});
      } catch (err: any) {
        console.error('Failed to clear emails:', err);
      }
    }
  };

  const handleAddEmails = async (newEmails: string[]) => {
    try {
      await fetch('/api/emails/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ emails: newEmails }),
      });
      fetchEmails();
    } catch (err: any) {
      console.error('Failed to add emails:', err);
    }
  };

  const handleSaveRawAccounts = async (raw: string) => {
    const res = await fetch('/api/accounts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ raw }),
    });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.error || 'Failed to save accounts');
    }
    await fetchAccounts();
  };

  const handleAddSingleAccount = async (email: string, password: string) => {
    const res = await fetch('/api/accounts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ account: { email, password } }),
    });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.error || 'Failed to add account');
    }
    await fetchAccounts();
  };

  const handleBatchValidate = async (emailsToValidate: string[]) => {
    if (emailsToValidate.length === 0 || isValidating) return;
    setIsValidating(true);
    setValidationProgress(0);

    const total = emailsToValidate.length;
    const batchSize = 10;
    const newResults: Record<string, ValidationItem> = { ...validationResults };

    for (let i = 0; i < total; i += batchSize) {
      const slice = emailsToValidate.slice(i, i + batchSize);
      await Promise.all(
        slice.map(async (email) => {
          try {
            const res = await fetch('/api/ai/validate-email', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ email }),
            });
            const data = await res.json();
            newResults[email] = data;
          } catch {
            newResults[email] = {
              email,
              status: 'INVALID',
              score: 0,
              detail: 'Validation request timed out',
            };
          }
        })
      );

      setValidationResults({ ...newResults });
      setValidationProgress(Math.round(((i + slice.length) / total) * 100));
    }

    setIsValidating(false);
  };

  const handleCleanBase = async () => {
    const badEmails = Object.values(validationResults)
      .filter(r => r.status === 'TRAP' || r.status === 'INVALID')
      .map(r => r.email.toLowerCase());

    if (badEmails.length === 0) return;

    const remaining = generalEmails.filter(e => !badEmails.includes(e.toLowerCase()));

    try {
      await fetch('/api/emails/clear', { method: 'POST' });
      await handleAddEmails(remaining);
      alert(`Удалено ${badEmails.length} ловушек и невалидных почт из базы.`);
    } catch (err: any) {
      alert(`Ошибка очистки базы: ${err.message}`);
    }
  };

  const verifiedList = generalEmails.filter(email => {
    const val = validationResults[email];
    if (!val) return true;
    return val.status === 'SAFE' || val.status === 'RISKY';
  });

  return (
    <div className="min-h-screen bg-[#050508] text-[#e0e0e0] flex relative overflow-x-hidden font-sans">
      {/* Background Audio Element for persistent playback */}
      <audio ref={audioRef} crossOrigin="anonymous" preload="none" />

      {/* Cyber Canvas Background */}
      <CyberBackground />

      {/* Main Left Sidebar with Lo-Fi Radio Tab */}
      <Sidebar
        currentTab={currentTab}
        onTabChange={setCurrentTab}
        isEngineRunning={crawlerStatus.running}
        isRadioPlaying={isRadioPlaying}
      />

      {/* Main Content Area */}
      <main className="flex-1 p-6 md:p-8 max-w-7xl mx-auto z-10 overflow-y-auto">
        {currentTab === 'dashboard' && (
          <Dashboard
            status={crawlerStatus}
            totalEmails={generalEmails.length}
            personalEmails={personalEmails.length}
            recentEmails={recentFeed}
            onStartSingle={() => handleStartCrawler(undefined, false, 40)}
            onStartInfinite={() => handleStartCrawler(undefined, true)}
            onStop={handleStopCrawler}
            onClear={handleClearDatabase}
          />
        )}

        {currentTab === 'crawler' && (
          <CrawlerPage
            status={crawlerStatus}
            onStartCrawler={handleStartCrawler}
            onStopCrawler={handleStopCrawler}
            onAddEmails={handleAddEmails}
          />
        )}

        {currentTab === 'validator' && (
          <ValidatorPage
            emails={generalEmails}
            validationResults={validationResults}
            onBatchValidate={handleBatchValidate}
            onCleanBase={handleCleanBase}
            isValidating={isValidating}
            progress={validationProgress}
          />
        )}

        {currentTab === 'mailer' && (
          <MailerPage
            accounts={accounts}
            verifiedEmails={verifiedList}
            onRefreshAccounts={fetchAccounts}
            onNavigateToAccounts={() => setCurrentTab('accounts')}
          />
        )}

        {currentTab === 'accounts' && (
          <AccountsPage
            accounts={accounts}
            rawAccountsText={rawAccountsText}
            onSaveRawAccounts={handleSaveRawAccounts}
            onAddAccount={handleAddSingleAccount}
            onRefresh={fetchAccounts}
          />
        )}

        {currentTab === 'lofi' && (
          <LofiRadioPage
            isPlaying={isRadioPlaying}
            onTogglePlay={toggleRadio}
            currentStation={currentStationId}
            onSelectStation={handleStationChange}
            volume={radioVolume}
            onVolumeChange={handleVolumeChange}
          />
        )}

        {currentTab === 'stats' && (
          <StatsPage
            totalEmails={generalEmails.length}
            personalEmails={personalEmails.length}
            allEmails={generalEmails}
            personalList={personalEmails}
            filePath={filePath}
            personalFilePath={personalFilePath}
            onAddManualEmails={handleAddEmails}
          />
        )}

        {currentTab === 'python' && <PythonScriptPage />}
      </main>
    </div>
  );
}
