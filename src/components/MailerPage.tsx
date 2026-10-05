import React, { useState } from 'react';
import {
  Mail,
  Sparkles,
  Send,
  ShieldCheck,
  AlertTriangle,
  Users,
  CheckCircle2,
  Terminal,
  X,
  RefreshCw,
  Info,
} from 'lucide-react';
import { RainbowLine, PulseDot } from './RainbowLine';
import { EmailAccount, PreflightResult } from '../types';

interface MailerPageProps {
  accounts: EmailAccount[];
  verifiedEmails: string[];
  onRefreshAccounts: () => void;
  onNavigateToAccounts: () => void;
}

export const MailerPage: React.FC<MailerPageProps> = ({
  accounts,
  verifiedEmails,
  onRefreshAccounts,
  onNavigateToAccounts,
}) => {
  // Sender account selected from accounts.txt
  const [selectedAccountEmail, setSelectedAccountEmail] = useState<string>(
    accounts[0]?.email || ''
  );

  // Recipient
  const [recipient, setRecipient] = useState<string>('');
  const [subject, setSubject] = useState<string>('Cooperation & Tech Collaboration Proposal');
  const [body, setBody] = useState<string>(`Hello,

I noticed your open-source projects and developer contributions. We are currently building advanced infrastructure and would love to discuss a potential partnership.

Would you be open for a short call this week?

Best regards,
Technical Outreach Team`);

  // AI Modal ("Воспользоваться ИИ")
  const [isAiModalOpen, setIsAiModalOpen] = useState<boolean>(false);
  const [aiPrompt, setAiPrompt] = useState<string>('Предложи сотрудничество по разработке программного обеспечения, укажи взаимную выгоду и вежливый призыв к действию');
  const [aiTone, setAiTone] = useState<string>('professional');
  const [aiLanguage, setAiLanguage] = useState<'ru' | 'en'>('ru');
  const [aiGenerating, setAiGenerating] = useState<boolean>(false);
  const [aiGeneratedPreview, setAiGeneratedPreview] = useState<{
    subject: string;
    body: string;
    tips?: string[];
  } | null>(null);

  // Pre-Flight Check & Sending
  const [isCheckingPreflight, setIsCheckingPreflight] = useState<boolean>(false);
  const [preflightModalOpen, setPreflightModalOpen] = useState<boolean>(false);
  const [preflightData, setPreflightData] = useState<PreflightResult | null>(null);
  const [isSending, setIsSending] = useState<boolean>(false);
  const [deliveryLogs, setDeliveryLogs] = useState<
    { id: string; time: string; message: string; type: 'info' | 'success' | 'warn' | 'err' }[]
  >([
    {
      id: '1',
      time: new Date().toTimeString().split(' ')[0],
      message: 'Mailer subsystem ready. Select sender account and recipient.',
      type: 'info',
    },
  ]);

  const activeAccount = accounts.find(a => a.email === selectedAccountEmail) || accounts[0];

  const addDeliveryLog = (message: string, type: 'info' | 'success' | 'warn' | 'err' = 'info') => {
    const time = new Date().toTimeString().split(' ')[0];
    setDeliveryLogs(prev => [
      { id: `${Date.now()}-${Math.random()}`, time, message, type },
      ...prev.slice(0, 100),
    ]);
  };

  // Generate Email with Gemini AI
  const handleGenerateWithAi = async () => {
    if (!aiPrompt.trim()) return;
    setAiGenerating(true);
    try {
      const res = await fetch('/api/ai/generate-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: aiPrompt.trim(),
          recipientEmail: recipient,
          tone: aiTone,
          language: aiLanguage,
          senderRole: 'Lead Specialist',
        }),
      });

      const data = await res.json();
      if (res.ok) {
        setAiGeneratedPreview({
          subject: data.subject || 'Cooperation Proposal',
          body: data.body || '',
          tips: data.tips || [],
        });
      } else {
        addDeliveryLog(`AI Generation error: ${data.error}`, 'err');
      }
    } catch (err: any) {
      addDeliveryLog(`Network error during AI drafting: ${err.message}`, 'err');
    } finally {
      setAiGenerating(false);
    }
  };

  const applyAiGeneratedEmail = () => {
    if (aiGeneratedPreview) {
      setSubject(aiGeneratedPreview.subject);
      setBody(aiGeneratedPreview.body);
      setIsAiModalOpen(false);
      addDeliveryLog('Applied AI-generated subject and body to mailer.', 'success');
    }
  };

  // Pre-Flight AI Check Before Send
  const handlePreflightCheck = async () => {
    if (!recipient.trim() || !body.trim()) {
      addDeliveryLog('Recipient and message body are required.', 'err');
      return;
    }
    if (!activeAccount) {
      addDeliveryLog('No sender account selected from accounts.txt.', 'err');
      return;
    }

    setIsCheckingPreflight(true);
    addDeliveryLog(`Running Gemini AI pre-flight inspection for ${recipient}...`, 'info');

    try {
      const res = await fetch('/api/ai/preflight-check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recipient: recipient.trim(),
          senderEmail: activeAccount.email,
          subject: subject.trim(),
          body: body.trim(),
        }),
      });

      const data = await res.json();
      setPreflightData(data);
      setPreflightModalOpen(true);
      addDeliveryLog(`Pre-flight verdict: ${data.verdict} (Spam Risk: ${data.spamScore}/100)`, data.verdict === 'PASS' ? 'success' : 'warn');
    } catch (err: any) {
      addDeliveryLog(`Pre-flight check error: ${err.message}`, 'err');
    } finally {
      setIsCheckingPreflight(false);
    }
  };

  // Confirm Dispatch
  const handleExecuteSend = async () => {
    if (!activeAccount) return;
    setIsSending(true);
    setPreflightModalOpen(false);
    addDeliveryLog(`Connecting to SMTP relay for ${activeAccount.email}...`, 'info');

    try {
      const res = await fetch('/api/mailer/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          senderEmail: activeAccount.email,
          senderPassword: activeAccount.password,
          recipient: recipient.trim(),
          subject: subject.trim(),
          body: body.trim(),
        }),
      });

      const data = await res.json();
      if (res.ok) {
        addDeliveryLog(`Delivered message to ${recipient} via ${activeAccount.email}. Message-ID: ${data.messageId}`, 'success');
      } else {
        addDeliveryLog(`Transmission failed: ${data.error}`, 'err');
      }
    } catch (err: any) {
      addDeliveryLog(`Network error while sending: ${err.message}`, 'err');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-extrabold text-white tracking-wider flex items-center gap-3">
              <Mail className="w-7 h-7 text-[#00f3ff]" />
              <span>AI Mailer & Delivery Studio</span>
            </h2>
            <p className="text-xs text-[#8a8aa0] mt-1 font-mono">
              Multi-account combo dispatch with Gemini AI drafting, spam shield evaluation, and RFC5322 compliance
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono px-3 py-1.5 rounded-lg bg-[#00ff9d]/10 text-[#00ff9d] border border-[#00ff9d]/30 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Anti-Spam Pre-Flight Armed</span>
            </span>
          </div>
        </div>
        <RainbowLine className="mt-4" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Accounts & Recipient Selector */}
        <div className="space-y-5">
          {/* Sender Account Card (Selected from accounts.txt) */}
          <div className="glass-panel p-5 rounded-2xl border border-[#8a2be2]/30 space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-xs font-mono uppercase text-[#00f3ff] font-bold flex items-center gap-2">
                <Users className="w-3.5 h-3.5" />
                <span>Sender Account (From accounts.txt)</span>
              </label>
              <button
                onClick={onRefreshAccounts}
                className="text-[11px] text-[#8a8aa0] hover:text-[#00f3ff] font-mono flex items-center gap-1"
              >
                <RefreshCw className="w-3 h-3" />
                <span>Sync</span>
              </button>
            </div>

            {accounts.length === 0 ? (
              <div className="p-4 rounded-xl bg-[#ff2a6d]/10 border border-[#ff2a6d]/30 text-center space-y-2">
                <p className="text-xs font-mono text-[#ff2a6d]">
                  No accounts found in accounts.txt!
                </p>
                <button
                  onClick={onNavigateToAccounts}
                  className="px-3 py-1.5 rounded-lg bg-[#ff2a6d]/20 text-white font-mono text-xs font-bold"
                >
                  Configure accounts.txt
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                <select
                  value={selectedAccountEmail || activeAccount?.email}
                  onChange={(e) => setSelectedAccountEmail(e.target.value)}
                  className="w-full bg-[#050508] text-white font-mono text-xs px-3.5 py-3 rounded-xl border border-[#8a2be2]/40 focus:border-[#00f3ff] outline-none"
                >
                  {accounts.map((acc, idx) => (
                    <option key={idx} value={acc.email}>
                      {acc.email} ({acc.provider})
                    </option>
                  ))}
                </select>

                <div className="p-3 rounded-xl bg-[#050508]/80 border border-[#8a2be2]/20 font-mono text-[11px] space-y-1">
                  <div className="flex justify-between text-[#8a8aa0]">
                    <span>Detected Provider:</span>
                    <span className="text-[#00ff9d] font-bold uppercase">{activeAccount?.provider}</span>
                  </div>
                  <div className="flex justify-between text-[#8a8aa0]">
                    <span>Security / Password:</span>
                    <span className="text-white">•••••••• (Loaded from file)</span>
                  </div>
                </div>

                <button
                  onClick={onNavigateToAccounts}
                  className="w-full py-2 rounded-lg bg-[#8a2be2]/15 hover:bg-[#8a2be2]/25 text-[#c084fc] font-mono text-xs flex items-center justify-center gap-1.5 border border-[#8a2be2]/30"
                >
                  <Users className="w-3.5 h-3.5" />
                  <span>Manage / Edit accounts.txt</span>
                </button>
              </div>
            )}
          </div>

          {/* Quick Recipient Picker from Harvested Base */}
          <div className="glass-panel p-5 rounded-2xl border border-[#8a2be2]/30 space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-xs font-mono uppercase text-[#00ff9d] font-bold flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Verified Database Recipients</span>
              </label>
              <span className="text-[11px] font-mono text-[#6a6a80]">
                {verifiedEmails.length} in base
              </span>
            </div>

            <div className="max-h-56 overflow-y-auto rounded-xl border border-[#8a2be2]/20 bg-[#050508]/70 p-2 space-y-1">
              {verifiedEmails.length === 0 ? (
                <div className="p-4 text-center text-[11px] font-mono text-[#6a6a80]">
                  No harvested emails yet. Run spider crawler or add emails in Database tab.
                </div>
              ) : (
                verifiedEmails.slice(0, 50).map((em, idx) => (
                  <button
                    key={idx}
                    onClick={() => setRecipient(em)}
                    className={`w-full text-left font-mono text-xs px-2.5 py-1.5 rounded-lg truncate transition-colors flex items-center justify-between ${
                      recipient === em
                        ? 'bg-[#00f3ff]/20 text-[#00f3ff] border border-[#00f3ff]/40'
                        : 'text-[#b0b0c0] hover:bg-[#8a2be2]/15 hover:text-white'
                    }`}
                  >
                    <span className="truncate">{em}</span>
                    <span className="text-[10px] text-[#6a6a80]">pick</span>
                  </button>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Column (2 spans): Message Composer + AI Button */}
        <div className="lg:col-span-2 space-y-5">
          <div className="glass-panel p-6 rounded-2xl border border-[#8a2be2]/30 space-y-4">
            {/* Recipient Input */}
            <div className="space-y-1.5">
              <label className="text-xs font-mono uppercase text-[#8a8aa0] font-bold">
                Recipient Email (TO:)
              </label>
              <input
                type="email"
                value={recipient}
                onChange={(e) => setRecipient(e.target.value)}
                placeholder="contact@targetdomain.com"
                className="w-full bg-[#050508] text-white font-mono text-xs px-4 py-2.5 rounded-xl border border-[#8a2be2]/35 focus:border-[#00f3ff] outline-none"
              />
            </div>

            {/* Subject Line */}
            <div className="space-y-1.5">
              <label className="text-xs font-mono uppercase text-[#8a8aa0] font-bold">
                Email Subject Line
              </label>
              <input
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="Subject of the email..."
                className="w-full bg-[#050508] text-white font-mono text-xs px-4 py-2.5 rounded-xl border border-[#8a2be2]/35 focus:border-[#00f3ff] outline-none"
              />
            </div>

            {/* Message Body with "Воспользоваться ИИ" Button */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-mono uppercase text-[#8a8aa0] font-bold">
                  Message Content (MIME / Plain / HTML)
                </label>

                {/* THE REQUESTED "ВОСПОЛЬЗОВАТЬСЯ ИИ" BUTTON */}
                <button
                  type="button"
                  onClick={() => setIsAiModalOpen(true)}
                  className="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-[#8a2be2] to-[#00f3ff] text-white text-xs font-mono font-bold uppercase tracking-wider flex items-center gap-2 hover:opacity-95 shadow-[0_0_15px_rgba(0,243,255,0.3)] transition-all transform hover:scale-[1.02]"
                >
                  <Sparkles className="w-3.5 h-3.5 text-[#00ff9d]" />
                  <span>Воспользоваться ИИ</span>
                </button>
              </div>

              <textarea
                rows={9}
                value={body}
                onChange={(e) => setBody(e.target.value)}
                placeholder="Write your email message here or click 'Воспользоваться ИИ' to auto-generate high-conversion text..."
                className="w-full bg-[#050508] text-[#e0e0e0] font-mono text-xs p-4 rounded-xl border border-[#8a2be2]/35 focus:border-[#00f3ff] outline-none resize-none leading-relaxed"
              />
            </div>

            {/* Action Bar */}
            <div className="flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-[#8a2be2]/20">
              <div className="flex items-center gap-2 text-xs font-mono text-[#8a8aa0]">
                <Info className="w-4 h-4 text-[#00f3ff]" />
                <span>Anti-Spam AI Check will audit the message before dispatch</span>
              </div>

              <button
                onClick={handlePreflightCheck}
                disabled={isCheckingPreflight || isSending || !recipient.trim()}
                className="px-6 py-3 rounded-xl bg-[#00ff9d]/20 hover:bg-[#00ff9d]/30 text-[#00ff9d] border border-[#00ff9d]/50 font-mono text-xs font-bold uppercase tracking-wider flex items-center gap-2 shadow-[0_0_20px_rgba(0,255,157,0.2)] disabled:opacity-40"
              >
                {isCheckingPreflight ? (
                  <PulseDot color="green" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
                <span>{isCheckingPreflight ? 'AI Auditing...' : 'AI Pre-Flight & Send'}</span>
              </button>
            </div>
          </div>

          {/* Delivery & Transmission Log Terminal */}
          <div className="glass-panel p-5 rounded-2xl border border-[#8a2be2]/30 space-y-3">
            <div className="flex items-center gap-2.5">
              <Terminal className="w-4 h-4 text-[#ffcc00]" />
              <h3 className="text-xs font-mono uppercase font-bold text-white tracking-wider">
                MAILER DISPATCH LOG // LIVE TRANSMISSION
              </h3>
            </div>

            <div className="h-44 overflow-y-auto rounded-xl bg-[#050508]/90 border border-[#8a2be2]/25 p-3 font-mono text-xs space-y-1">
              {deliveryLogs.map((log) => {
                const color = {
                  info: 'text-[#00f3ff]',
                  success: 'text-[#00ff9d]',
                  warn: 'text-[#ffcc00]',
                  err: 'text-[#ff2a6d]',
                }[log.type];
                return (
                  <div key={log.id} className="leading-relaxed flex items-start gap-2">
                    <span className="text-[#6a6a80] shrink-0">[{log.time}]</span>
                    <span className={color}>{log.message}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* MODAL 1: "Воспользоваться ИИ" (Use AI Prompt Drawer) */}
      {isAiModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-2xl rounded-2xl border border-[#00f3ff]/40 p-6 space-y-5 shadow-[0_0_40px_rgba(0,243,255,0.25)] relative max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-[#8a2be2]/25 pb-3">
              <div className="flex items-center gap-2.5">
                <Sparkles className="w-5 h-5 text-[#00f3ff]" />
                <h3 className="text-base font-bold text-white font-mono tracking-wide">
                  Генератор Писем Gemini AI
                </h3>
              </div>
              <button
                onClick={() => setIsAiModalOpen(false)}
                className="p-1 rounded-lg text-[#8a8aa0] hover:text-white hover:bg-white/10"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-mono text-[#00f3ff] font-bold uppercase">
                  Какого рода текст и предложение вам нужно? (Опишите задачу)
                </label>
                <textarea
                  rows={4}
                  value={aiPrompt}
                  onChange={(e) => setAiPrompt(e.target.value)}
                  placeholder="Например: 'Напиши персональное предложение о сотрудничестве для разработчика на Go, отметь интерес к его репозиториям и предложи обсудить проект в Telegram'..."
                  className="w-full bg-[#050508] text-white font-mono text-xs p-3.5 rounded-xl border border-[#8a2be2]/40 focus:border-[#00f3ff] outline-none"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-xs font-mono text-[#8a8aa0]">Тон сообщения:</label>
                  <select
                    value={aiTone}
                    onChange={(e) => setAiTone(e.target.value)}
                    className="w-full bg-[#050508] text-white font-mono text-xs p-2.5 rounded-xl border border-[#8a2be2]/30"
                  >
                    <option value="professional">Деловой и уважительный (Professional)</option>
                    <option value="friendly">Дружелюбный и открытый (Friendly / Dev-to-Dev)</option>
                    <option value="persuasive">Убедительный B2B (High Conversion)</option>
                    <option value="concise">Краткий и по делу (Under 100 words)</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-mono text-[#8a8aa0]">Язык:</label>
                  <select
                    value={aiLanguage}
                    onChange={(e) => setAiLanguage(e.target.value as any)}
                    className="w-full bg-[#050508] text-white font-mono text-xs p-2.5 rounded-xl border border-[#8a2be2]/30"
                  >
                    <option value="ru">Русский (Russian)</option>
                    <option value="en">English (International)</option>
                  </select>
                </div>
              </div>

              <button
                onClick={handleGenerateWithAi}
                disabled={aiGenerating || !aiPrompt.trim()}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-[#8a2be2] to-[#00f3ff] text-white font-mono text-xs font-bold uppercase tracking-wider flex items-center justify-center gap-2 disabled:opacity-40 shadow-[0_0_20px_rgba(138,43,226,0.3)]"
              >
                {aiGenerating ? <PulseDot color="cyan" /> : <Sparkles className="w-4 h-4" />}
                <span>{aiGenerating ? 'Нейросеть генерирует текст...' : 'Сгенерировать Текст Письма'}</span>
              </button>

              {/* Generated Result Preview */}
              {aiGeneratedPreview && (
                <div className="p-4 rounded-xl bg-[#050508] border border-[#00ff9d]/30 space-y-3 font-mono text-xs">
                  <div>
                    <span className="text-[#8a8aa0] block text-[10px] uppercase font-bold">Тема:</span>
                    <span className="text-[#00f3ff] font-bold text-sm">{aiGeneratedPreview.subject}</span>
                  </div>

                  <div>
                    <span className="text-[#8a8aa0] block text-[10px] uppercase font-bold">Текст письма:</span>
                    <p className="text-white whitespace-pre-wrap mt-1 leading-relaxed bg-[#0c0816] p-3 rounded-lg border border-[#8a2be2]/20">
                      {aiGeneratedPreview.body}
                    </p>
                  </div>

                  <button
                    onClick={applyAiGeneratedEmail}
                    className="w-full py-2.5 rounded-xl bg-[#00ff9d]/20 hover:bg-[#00ff9d]/30 text-[#00ff9d] border border-[#00ff9d]/50 font-bold uppercase tracking-wider text-xs"
                  >
                    Вставить в форму отправки
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* MODAL 2: Pre-Flight AI Check Results before sending */}
      {preflightModalOpen && preflightData && (
        <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-lg rounded-2xl border border-[#00ff9d]/40 p-6 space-y-4 shadow-[0_0_40px_rgba(0,255,157,0.25)]">
            <div className="flex items-center justify-between border-b border-[#8a2be2]/25 pb-3">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-[#00ff9d]" />
                <h3 className="text-base font-bold text-white font-mono">
                  Gemini AI Pre-Flight Audit Result
                </h3>
              </div>
              <button
                onClick={() => setPreflightModalOpen(false)}
                className="text-[#8a8aa0] hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div className="flex items-center justify-between p-3 rounded-xl bg-[#050508] border border-[#8a2be2]/30">
                <span className="text-[#8a8aa0]">Deliverability Verdict:</span>
                <span
                  className={`px-2.5 py-1 rounded font-bold uppercase ${
                    preflightData.verdict === 'PASS'
                      ? 'bg-[#00ff9d]/20 text-[#00ff9d] border border-[#00ff9d]/40'
                      : 'bg-[#ffcc00]/20 text-[#ffcc00] border border-[#ffcc00]/40'
                  }`}
                >
                  {preflightData.verdict}
                </span>
              </div>

              <div className="flex items-center justify-between p-3 rounded-xl bg-[#050508] border border-[#8a2be2]/30">
                <span className="text-[#8a8aa0]">Spam Risk Score:</span>
                <span className="text-sm font-bold text-white">
                  {preflightData.spamScore} / 100
                </span>
              </div>

              {preflightData.summary && (
                <p className="text-[#e0e0e0] bg-[#0c0816] p-3 rounded-xl border border-[#8a2be2]/20">
                  {preflightData.summary}
                </p>
              )}

              {preflightData.warnings && preflightData.warnings.length > 0 && (
                <div className="p-3 rounded-xl bg-[#ff2a6d]/10 border border-[#ff2a6d]/30 text-[#ff2a6d] space-y-1">
                  <span className="font-bold block">Warnings:</span>
                  {preflightData.warnings.map((w, idx) => (
                    <div key={idx}>• {w}</div>
                  ))}
                </div>
              )}
            </div>

            <div className="flex gap-3 pt-2">
              <button
                onClick={() => setPreflightModalOpen(false)}
                className="flex-1 py-2.5 rounded-xl bg-[#050508] text-[#8a8aa0] hover:text-white font-mono text-xs font-bold"
              >
                Edit Message
              </button>
              <button
                onClick={handleExecuteSend}
                disabled={isSending}
                className="flex-1 py-2.5 rounded-xl bg-[#00ff9d]/25 hover:bg-[#00ff9d]/35 text-[#00ff9d] border border-[#00ff9d]/50 font-mono text-xs font-bold uppercase tracking-wider"
              >
                {isSending ? 'Sending...' : 'Confirm & Dispatch'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
