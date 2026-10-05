import React, { useState, useEffect, useRef } from 'react';
import {
  Radio,
  Volume2,
  VolumeX,
  Play,
  Square,
  Sparkles,
  Music,
  CloudRain,
  Disc3,
  Sliders,
  Headphones,
} from 'lucide-react';
import { RainbowLine, PulseDot } from './RainbowLine';

interface LofiRadioProps {
  isPlaying: boolean;
  onTogglePlay: () => void;
  currentStation: string;
  onSelectStation: (stationId: string) => void;
  volume: number;
  onVolumeChange: (vol: number) => void;
}

export const STATIONS = [
  {
    id: 'lofi-hiphop',
    name: 'Lofi Chillhop & Study Beats',
    tag: 'CHILLHOP',
    url: 'https://stream.laut.fm/lofi',
    desc: 'Relaxing hip-hop beats, mellow rhodes keys, and dusty vinyl groove',
  },
  {
    id: 'plaza-vapor',
    name: 'Nightwave Plaza & Vaporwave',
    tag: 'VAPORWAVE',
    url: 'https://radio.plaza.one/mp3',
    desc: 'Nostalgic 80s aesthetics, synthwave pads, and late-night cyberpunk echoes',
  },
  {
    id: 'groove-salad',
    name: 'SomaFM Groove Salad',
    tag: 'AMBIENT LOFI',
    url: 'https://ice1.somafm.com/groovesalad-128-mp3',
    desc: 'Downtempo ambient grooves, smooth chilled electronic textures',
  },
  {
    id: 'lush-chill',
    name: 'Lush Chilled Electronic',
    tag: 'DOWNTEMPO',
    url: 'https://ice1.somafm.com/lush-128-mp3',
    desc: 'Sensuous and soothing mellow beats, warm vocal atmospheres',
  },
];

export const LofiRadioPage: React.FC<LofiRadioProps> = ({
  isPlaying,
  onTogglePlay,
  currentStation,
  onSelectStation,
  volume,
  onVolumeChange,
}) => {
  const [rainEnabled, setRainEnabled] = useState<boolean>(false);
  const [vinylCrackle, setVinylCrackle] = useState<boolean>(true);
  const visualizerCanvasRef = useRef<HTMLCanvasElement | null>(null);

  // Canvas visualizer animation
  useEffect(() => {
    const canvas = visualizerCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    const barCount = 48;
    const bars: number[] = Array.from({ length: barCount }, () => Math.random() * 20);

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const width = canvas.width;
      const height = canvas.height;
      const barWidth = width / barCount - 2;

      for (let i = 0; i < barCount; i++) {
        if (isPlaying) {
          // Dynamic wave when playing
          bars[i] += (Math.random() - 0.5) * 8;
          bars[i] = Math.max(4, Math.min(height - 10, bars[i] + Math.sin(Date.now() / 200 + i * 0.3) * 3));
        } else {
          // Idle flat line
          bars[i] = Math.max(3, bars[i] * 0.95);
        }

        const h = bars[i];
        const x = i * (barWidth + 2);
        const y = height - h;

        const grad = ctx.createLinearGradient(0, y, 0, height);
        grad.addColorStop(0, '#00f3ff');
        grad.addColorStop(0.5, '#8a2be2');
        grad.addColorStop(1, '#00ff9d');

        ctx.fillStyle = grad;
        ctx.fillRect(x, y, barWidth, h);
      }

      animId = requestAnimationFrame(render);
    };

    render();

    return () => cancelAnimationFrame(animId);
  }, [isPlaying]);

  const activeStationObj = STATIONS.find(s => s.id === currentStation) || STATIONS[0];

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-extrabold text-white tracking-wider flex items-center gap-3">
              <Radio className="w-7 h-7 text-[#00f3ff] animate-pulse" />
              <span>Cyberpunk Lo-Fi Radio</span>
            </h2>
            <p className="text-xs text-[#8a8aa0] mt-1 font-mono">
              Live streaming lofi beats, ambient chillhop, and atmospheric textures for deep focus OSINT sessions
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span
              className={`text-xs font-mono px-3 py-1.5 rounded-lg border flex items-center gap-2 ${
                isPlaying
                  ? 'bg-[#00ff9d]/10 border-[#00ff9d]/30 text-[#00ff9d]'
                  : 'bg-[#0c0816] border-[#8a2be2]/30 text-[#6a6a80]'
              }`}
            >
              <PulseDot color={isPlaying ? 'green' : 'purple'} active={isPlaying} />
              <span>{isPlaying ? 'ON AIR' : 'RADIO OFF'}</span>
            </span>
          </div>
        </div>
        <RainbowLine className="mt-4" />
      </div>

      {/* Main Boombox / Player Card */}
      <div className="glass-panel p-8 rounded-3xl border border-[#8a2be2]/40 relative overflow-hidden space-y-6 shadow-[0_0_35px_rgba(138,43,226,0.2)]">
        {/* Subtle background glow */}
        <div className="absolute -top-24 -right-24 w-80 h-80 bg-[#00f3ff]/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-80 h-80 bg-[#8a2be2]/15 rounded-full blur-3xl pointer-events-none" />

        {/* Cassette / Audio Visualizer Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-mono">
            <div className="flex items-center gap-2 text-[#00f3ff]">
              <Disc3 className={`w-4 h-4 ${isPlaying ? 'animate-spin' : ''}`} />
              <span className="font-bold uppercase tracking-wider">{activeStationObj.name}</span>
            </div>
            <span className="text-[#8a8aa0]">{isPlaying ? 'STREAMING 128KBPS MP3' : 'STOPPED'}</span>
          </div>

          <div className="h-28 w-full bg-[#050508]/90 rounded-2xl border border-[#8a2be2]/35 p-3 flex items-end relative overflow-hidden">
            <canvas
              ref={visualizerCanvasRef}
              width={640}
              height={100}
              className="w-full h-full"
            />
          </div>
        </div>

        {/* Center Big "Turn on" / "Turn off" Button */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-6 pt-2">
          <div className="flex items-center gap-4">
            <button
              onClick={onTogglePlay}
              className={`px-8 py-4 rounded-2xl font-mono text-sm font-black uppercase tracking-widest flex items-center gap-3 transition-all transform hover:scale-105 ${
                isPlaying
                  ? 'bg-gradient-to-r from-[#ff2a6d] to-[#b026ff] text-white shadow-[0_0_30px_rgba(255,42,109,0.4)] border border-[#ff2a6d]/60'
                  : 'bg-gradient-to-r from-[#00f3ff] via-[#8a2be2] to-[#00ff9d] text-black shadow-[0_0_35px_rgba(0,243,255,0.45)] border border-[#00f3ff]/60'
              }`}
            >
              {isPlaying ? (
                <>
                  <Square className="w-5 h-5 fill-current" />
                  <span>Turn off</span>
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 fill-current" />
                  <span>Turn on</span>
                </>
              )}
            </button>

            <div className="text-xs font-mono">
              <div className="text-white font-bold tracking-wide">
                {isPlaying ? 'Playing in background' : 'Click to start Lo-Fi stream'}
              </div>
              <div className="text-[#6a6a80] text-[11px] mt-0.5">
                Music continues playing even when switching tabs
              </div>
            </div>
          </div>

          {/* Volume Control */}
          <div className="flex items-center gap-3 bg-[#050508]/80 px-4 py-3 rounded-xl border border-[#8a2be2]/25">
            <button
              onClick={() => onVolumeChange(volume === 0 ? 0.7 : 0)}
              className="text-[#8a8aa0] hover:text-[#00f3ff]"
            >
              {volume === 0 ? <VolumeX className="w-4 h-4 text-[#ff2a6d]" /> : <Volume2 className="w-4 h-4 text-[#00f3ff]" />}
            </button>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={volume}
              onChange={(e) => onVolumeChange(parseFloat(e.target.value))}
              className="w-28 accent-[#00f3ff] cursor-pointer"
            />
            <span className="text-[11px] font-mono text-[#8a8aa0] w-8 text-right">
              {Math.round(volume * 100)}%
            </span>
          </div>
        </div>

        {/* Atmosphere Effect Toggles */}
        <div className="flex flex-wrap items-center gap-3 pt-4 border-t border-[#8a2be2]/20">
          <span className="text-xs font-mono uppercase font-bold text-[#8a8aa0] flex items-center gap-1.5 mr-2">
            <Sliders className="w-3.5 h-3.5 text-[#00f3ff]" />
            <span>Atmosphere FX:</span>
          </span>

          <button
            onClick={() => setVinylCrackle(!vinylCrackle)}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono flex items-center gap-2 border transition-all ${
              vinylCrackle
                ? 'bg-[#8a2be2]/20 text-[#00f3ff] border-[#00f3ff]/40 shadow-[0_0_10px_rgba(0,243,255,0.2)]'
                : 'bg-[#050508] text-[#6a6a80] border-[#8a2be2]/20'
            }`}
          >
            <Disc3 className="w-3.5 h-3.5" />
            <span>Vinyl Warmth & Crackle</span>
          </button>

          <button
            onClick={() => setRainEnabled(!rainEnabled)}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono flex items-center gap-2 border transition-all ${
              rainEnabled
                ? 'bg-[#00ff9d]/20 text-[#00ff9d] border-[#00ff9d]/40 shadow-[0_0_10px_rgba(0,255,157,0.2)]'
                : 'bg-[#050508] text-[#6a6a80] border-[#8a2be2]/20'
            }`}
          >
            <CloudRain className="w-3.5 h-3.5" />
            <span>Rain Sound Filter</span>
          </button>
        </div>
      </div>

      {/* Station Selector Cards */}
      <div className="space-y-3">
        <h3 className="text-xs font-mono uppercase font-bold text-[#b026ff] flex items-center gap-2">
          <Headphones className="w-3.5 h-3.5 text-[#00f3ff]" />
          <span>Curated Lo-Fi Stations & Moods</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {STATIONS.map((station) => {
            const isSelected = station.id === currentStation;
            return (
              <div
                key={station.id}
                onClick={() => onSelectStation(station.id)}
                className={`glass-panel p-5 rounded-2xl border cursor-pointer transition-all flex flex-col justify-between space-y-3 ${
                  isSelected
                    ? 'border-[#00f3ff] bg-[#8a2be2]/15 shadow-[0_0_20px_rgba(0,243,255,0.2)]'
                    : 'border-[#8a2be2]/20 hover:border-[#8a2be2]/40 bg-[#0c0816]/50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <Music className={`w-4 h-4 ${isSelected ? 'text-[#00f3ff]' : 'text-[#6a6a80]'}`} />
                    <span className="font-mono text-sm font-bold text-white tracking-wide">
                      {station.name}
                    </span>
                  </div>
                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase tracking-wider ${
                      isSelected
                        ? 'bg-[#00f3ff]/20 text-[#00f3ff] border border-[#00f3ff]/40'
                        : 'bg-[#050508] text-[#6a6a80]'
                    }`}
                  >
                    {station.tag}
                  </span>
                </div>

                <p className="text-xs text-[#8a8aa0] font-mono leading-relaxed">
                  {station.desc}
                </p>

                <div className="flex items-center justify-between pt-2 border-t border-[#8a2be2]/15 text-[11px] font-mono">
                  <span className={isSelected ? 'text-[#00ff9d] font-bold' : 'text-[#6a6a80]'}>
                    {isSelected ? (isPlaying ? 'Active Playing Stream' : 'Selected Station') : 'Click to select'}
                  </span>
                  <span className="text-[#00f3ff]">128kbps</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
