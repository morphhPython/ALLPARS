import React from 'react';
import {
  LayoutDashboard,
  Terminal,
  CheckCircle2,
  Mail,
  Users,
  BarChart3,
  Code2,
  Radio,
  Headphones,
} from 'lucide-react';
import { PulseDot } from './RainbowLine';

export type TabKey =
  | 'dashboard'
  | 'crawler'
  | 'validator'
  | 'mailer'
  | 'accounts'
  | 'lofi'
  | 'stats'
  | 'python';

interface SidebarProps {
  currentTab: TabKey;
  onTabChange: (tab: TabKey) => void;
  isEngineRunning: boolean;
  isRadioPlaying: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onTabChange,
  isEngineRunning,
  isRadioPlaying,
}) => {
  const navItems: { key: TabKey; label: string; icon: React.ReactNode; badge?: string }[] = [
    { key: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
    { key: 'crawler', label: 'Spider & Dorks', icon: <Terminal className="w-4 h-4" />, badge: 'SPIDER' },
    { key: 'validator', label: 'AI Validator', icon: <CheckCircle2 className="w-4 h-4" />, badge: 'GEMINI' },
    { key: 'mailer', label: 'AI Mailer', icon: <Mail className="w-4 h-4" />, badge: 'SMART' },
    { key: 'accounts', label: 'Combo Accounts', icon: <Users className="w-4 h-4" /> },
    { key: 'lofi', label: 'Lo-Fi Radio', icon: <Headphones className="w-4 h-4" />, badge: isRadioPlaying ? 'LIVE' : undefined },
    { key: 'stats', label: 'Database & Base', icon: <BarChart3 className="w-4 h-4" /> },
    { key: 'python', label: 'Desktop Python', icon: <Code2 className="w-4 h-4" /> },
  ];

  return (
    <aside className="w-64 min-h-screen bg-[#0c0816]/85 backdrop-blur-md border-r border-[#8a2be2]/25 flex flex-col justify-between p-5 z-20 shrink-0">
      <div>
        {/* Animated Brand Logo */}
        <div className="pt-2 pb-6 text-center">
          <div className="inline-block relative">
            <h1 className="text-3xl font-black tracking-widest bg-gradient-to-r from-[#00f3ff] via-[#b026ff] to-[#00ff9d] bg-clip-text text-transparent drop-shadow-[0_0_15px_rgba(138,43,226,0.8)] font-mono animate-pulse">
              MORPHH
            </h1>
            <span className="text-[10px] font-mono text-[#6a6a80] tracking-widest block uppercase mt-0.5">
              ALLPARSv1.3 // AI OSINT
            </span>
          </div>
        </div>

        {/* Navigation list */}
        <nav className="space-y-1.5 mt-2">
          {navItems.map((item) => {
            const isActive = currentTab === item.key;
            return (
              <button
                key={item.key}
                onClick={() => onTabChange(item.key)}
                className={`w-full flex items-center justify-between px-3.5 py-3 rounded-xl text-xs font-semibold tracking-wide transition-all duration-200 text-left ${
                  isActive
                    ? 'bg-gradient-to-r from-[#8a2be2]/30 to-[#b026ff]/20 text-[#00f3ff] border-l-4 border-[#00f3ff] shadow-[0_0_20px_rgba(138,43,226,0.3)]'
                    : 'text-[#8a8aa0] hover:text-[#d0d0e0] hover:bg-[#8a2be2]/10 border-l-4 border-transparent'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className={isActive ? 'text-[#00f3ff]' : 'text-[#6a6a80]'}>
                    {item.icon}
                  </span>
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={`text-[9px] px-1.5 py-0.5 rounded font-mono font-bold uppercase tracking-wider ${
                      item.badge === 'LIVE'
                        ? 'bg-[#00ff9d]/20 text-[#00ff9d] border border-[#00ff9d]/40 animate-pulse'
                        : item.badge === 'GEMINI'
                        ? 'bg-[#00f3ff]/15 text-[#00f3ff] border border-[#00f3ff]/30'
                        : 'bg-[#8a2be2]/20 text-[#c084fc] border border-[#8a2be2]/30'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Engine & Radio Status Deck */}
      <div className="mt-8 pt-4 border-t border-[#8a2be2]/20 space-y-2.5">
        {/* Lo-Fi Radio Pill */}
        <div
          onClick={() => onTabChange('lofi')}
          className={`cursor-pointer flex items-center justify-between px-3 py-2 rounded-lg border transition-all ${
            isRadioPlaying
              ? 'bg-[#00ff9d]/10 border-[#00ff9d]/30 text-[#00ff9d]'
              : 'bg-[#050508]/60 border-[#8a2be2]/15 text-[#6a6a80] hover:text-[#b0b0c0]'
          }`}
        >
          <div className="flex items-center gap-2">
            <Radio className={`w-3.5 h-3.5 ${isRadioPlaying ? 'text-[#00ff9d] animate-pulse' : 'text-[#6a6a80]'}`} />
            <span className="font-mono text-[10px] uppercase font-bold tracking-wider">
              {isRadioPlaying ? 'LO-FI PLAYING' : 'LO-FI RADIO OFF'}
            </span>
          </div>
          <span className="text-[9px] font-mono opacity-80">
            {isRadioPlaying ? 'ON' : 'OPEN'}
          </span>
        </div>

        {/* Crawler Status Pill */}
        <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-[#050508]/60 border border-[#8a2be2]/15">
          <div className="flex items-center gap-2">
            <PulseDot
              color={isEngineRunning ? 'green' : 'purple'}
              active={isEngineRunning}
            />
            <span className="font-mono text-[10px] uppercase tracking-wider font-bold text-[#b0b0c0]">
              {isEngineRunning ? 'ENGINE RUNNING' : 'ENGINE IDLE'}
            </span>
          </div>
          <span className="font-mono text-[9px] text-[#6a6a80]">SPIDER</span>
        </div>

        <div className="text-center font-mono text-[10px] text-[#4a4a5a]">
          AI STUDIO FULL-STACK v2.0
        </div>
      </div>
    </aside>
  );
};
