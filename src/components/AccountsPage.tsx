import React, { useState } from 'react';
import { Users, Plus, Save, FileText, Check, AlertCircle, Key, RefreshCw } from 'lucide-react';
import { RainbowLine } from './RainbowLine';
import { EmailAccount } from '../types';

interface AccountsPageProps {
  accounts: EmailAccount[];
  rawAccountsText: string;
  onSaveRawAccounts: (raw: string) => Promise<void>;
  onAddAccount: (email: string, pass: string) => Promise<void>;
  onRefresh: () => void;
}

export const AccountsPage: React.FC<AccountsPageProps> = ({
  accounts,
  rawAccountsText,
  onSaveRawAccounts,
  onAddAccount,
  onRefresh,
}) => {
  const [newEmail, setNewEmail] = useState<string>('');
  const [newPassword, setNewPassword] = useState<string>('');
  const [editorText, setEditorText] = useState<string>(rawAccountsText);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<{ text: string; type: 'success' | 'err' } | null>(null);

  // Sync if prop updates
  React.useEffect(() => {
    setEditorText(rawAccountsText);
  }, [rawAccountsText]);

  const handleAddSingle = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEmail.trim() || !newPassword.trim()) {
      setStatusMessage({ text: 'Please fill both email and password.', type: 'err' });
      return;
    }
    if (!newEmail.includes('@')) {
      setStatusMessage({ text: 'Invalid email address format.', type: 'err' });
      return;
    }

    try {
      await onAddAccount(newEmail.trim(), newPassword.trim());
      setNewEmail('');
      setNewPassword('');
      setStatusMessage({ text: `Account ${newEmail} saved to accounts.txt`, type: 'success' });
    } catch (err: any) {
      setStatusMessage({ text: err.message, type: 'err' });
    }
  };

  const handleSaveRaw = async () => {
    setIsSaving(true);
    setStatusMessage(null);
    try {
      await onSaveRawAccounts(editorText);
      setStatusMessage({ text: 'accounts.txt successfully saved to server storage.', type: 'success' });
    } catch (err: any) {
      setStatusMessage({ text: err.message, type: 'err' });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-extrabold text-white tracking-wider flex items-center gap-3">
              <Users className="w-7 h-7 text-[#00f3ff]" />
              <span>Sender Accounts Manager (accounts.txt)</span>
            </h2>
            <p className="text-xs text-[#8a8aa0] mt-1 font-mono">
              Saved combos formatted as <code className="text-[#00ff9d]">email:password</code> loaded directly into the Mailer dropdown
            </p>
          </div>
          <button
            onClick={onRefresh}
            className="text-xs font-mono px-3 py-1.5 rounded-lg bg-[#0c0816] text-[#00f3ff] border border-[#8a2be2]/30 flex items-center gap-1.5 hover:bg-[#8a2be2]/15"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reload File</span>
          </button>
        </div>
        <RainbowLine className="mt-4" />
      </div>

      {statusMessage && (
        <div
          className={`p-3.5 rounded-xl font-mono text-xs flex items-center gap-2 border ${
            statusMessage.type === 'success'
              ? 'bg-[#00ff9d]/10 text-[#00ff9d] border-[#00ff9d]/30'
              : 'bg-[#ff2a6d]/10 text-[#ff2a6d] border-[#ff2a6d]/30'
          }`}
        >
          {statusMessage.type === 'success' ? <Check className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
          <span>{statusMessage.text}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Quick Add + Active Accounts List */}
        <div className="space-y-5">
          {/* Quick Add Form */}
          <div className="glass-panel p-5 rounded-2xl border border-[#8a2be2]/30 space-y-4">
            <h3 className="text-xs font-mono uppercase font-bold text-[#00f3ff] flex items-center gap-2">
              <Plus className="w-3.5 h-3.5" />
              <span>Add Single Account</span>
            </h3>

            <form onSubmit={handleAddSingle} className="space-y-3 font-mono text-xs">
              <div className="space-y-1">
                <label className="text-[#8a8aa0]">Email Address:</label>
                <input
                  type="email"
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  placeholder="e.g. sender@gmail.com"
                  className="w-full bg-[#050508] text-white p-2.5 rounded-xl border border-[#8a2be2]/30 focus:border-[#00f3ff] outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[#8a8aa0]">Password / App Password:</label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="e.g. xxxx-xxxx-xxxx-xxxx"
                  className="w-full bg-[#050508] text-white p-2.5 rounded-xl border border-[#8a2be2]/30 focus:border-[#00f3ff] outline-none"
                />
              </div>

              <button
                type="submit"
                className="w-full py-2.5 rounded-xl bg-[#00f3ff]/20 hover:bg-[#00f3ff]/30 text-[#00f3ff] border border-[#00f3ff]/40 font-bold uppercase tracking-wider transition-colors flex items-center justify-center gap-2"
              >
                <Key className="w-3.5 h-3.5" />
                <span>Save to accounts.txt</span>
              </button>
            </form>
          </div>

          {/* Active Parsed Accounts */}
          <div className="glass-panel p-5 rounded-2xl border border-[#8a2be2]/30 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-mono uppercase font-bold text-[#b026ff] flex items-center gap-2">
                <Users className="w-3.5 h-3.5" />
                <span>Active Mailer Combos ({accounts.length})</span>
              </h3>
            </div>

            <div className="max-h-72 overflow-y-auto space-y-2">
              {accounts.length === 0 ? (
                <div className="p-4 text-center font-mono text-xs text-[#6a6a80]">
                  No valid email:password rows detected.
                </div>
              ) : (
                accounts.map((acc, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-xl bg-[#050508]/80 border border-[#8a2be2]/20 font-mono text-xs flex items-center justify-between"
                  >
                    <div>
                      <div className="text-[#00f3ff] font-semibold">{acc.email}</div>
                      <div className="text-[10px] text-[#8a8aa0]">
                        Provider: <span className="text-[#00ff9d] uppercase">{acc.provider}</span>
                      </div>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-[#00ff9d]/10 text-[#00ff9d] border border-[#00ff9d]/20">
                      READY
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Raw File Editor for data/accounts.txt */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-[#8a2be2]/30 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-[#00ff9d]" />
              <h3 className="text-xs font-mono uppercase font-bold text-white tracking-wider">
                Direct Raw Editor: data/accounts.txt
              </h3>
            </div>

            <button
              onClick={handleSaveRaw}
              disabled={isSaving}
              className="px-5 py-2.5 rounded-xl bg-[#00ff9d]/20 hover:bg-[#00ff9d]/30 text-[#00ff9d] border border-[#00ff9d]/40 font-mono text-xs font-bold uppercase tracking-wider flex items-center gap-2 disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              <span>{isSaving ? 'Saving...' : 'Save File (accounts.txt)'}</span>
            </button>
          </div>

          <div className="p-3 rounded-xl bg-[#050508] border border-[#8a2be2]/20 text-[11px] font-mono text-[#8a8aa0] leading-relaxed">
            Format: <code className="text-[#00f3ff]">email:password</code> (one per line). Lines starting with <code className="text-[#ffcc00]">#</code> are ignored.
            For Gmail or Yandex, generate an <strong className="text-white">App Password</strong> from your security settings instead of your regular master password.
          </div>

          <textarea
            rows={14}
            value={editorText}
            onChange={(e) => setEditorText(e.target.value)}
            className="w-full bg-[#050508]/95 text-[#00ff9d] font-mono text-xs p-4 rounded-xl border border-[#8a2be2]/35 focus:border-[#00f3ff] outline-none leading-relaxed"
            placeholder="# Format:&#10;user1@gmail.com:app_password_here&#10;user2@yandex.ru:pass1234"
          />
        </div>
      </div>
    </div>
  );
};
