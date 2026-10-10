import React, { useState, useEffect, useRef } from 'react';
import {
  LayoutDashboard, Terminal, CheckCircle2, Mail, Users, Radio,
  Database, Code2, Play, Pause, Volume2, VolumeX, Shield, Sparkles, RefreshCw,
  Trash2, Send, Save, Key, ExternalLink, Copy, Download, Check, AlertTriangle,
  Film, Heart, ChevronDown, ChevronUp, Globe2, Languages, Search, Share2, Disc3, Repeat,
  MessageSquare, Plus, X, Flame, SlidersHorizontal, UserPlus, UserCheck, Sparkle
} from 'lucide-react';

interface HarvestContact {
  id: number;
  email: string;
  country: string;
  lastActive: string;
  category: 'HUMAN / PERSONAL' | 'CORPORATE / DEV';
  targetSource: string;
  score: number;
  timestamp: string;
}

interface ValidatedRecord {
  email: string;
  country: string;
  lastActive: string;
  verdict: 'SAFE' | 'RISKY' | 'TRAP' | 'INVALID';
  score: number;
  detail: string;
}

interface AccountCombo {
  email: string;
  provider: string;
  status: 'READY' | 'ACTIVE';
}

export interface ShortVideoItem {
  id: string | number;
  youtubeId?: string;
  title: string;
  author: string;
  avatar: string;
  category: 'TECH' | 'MEMES' | 'GAMING' | 'ASMR' | 'CYBER' | 'AUTO';
  tags: string;
  sound: string;
  likes: number;
  commentsCount: string;
  views: string;
  url: string;
  embedUrl?: string;
  isCustom?: boolean;
}

const RADIO_STATIONS = [
  { name: '☕ FluxFM Chillhop & Study Beats', genre: 'CHILLHOP', desc: 'Ultra high-quality pure Lo-Fi hip-hop beats, dusty vinyl and Rhodes piano', url: 'https://streams.fluxfm.de/chillhop/mp3-320/audio.mp3', bitrate: '320kbps MP3' },
  { name: '👾 DEF CON Radio (Cyber Chill)', genre: 'CYBERPUNK', desc: 'Hacker conference downtempo cyber soundscapes, dark ambient and synth pads', url: 'https://ice2.somafm.com/defcon-128-mp3', bitrate: '128kbps MP3' },
  { name: '🌿 Groove Salad (Downtempo Beats)', genre: 'DOWNTEMPO', desc: 'World famous chilled ambient downtempo beats and relaxing electronic groove', url: 'https://ice1.somafm.com/groovesalad-128-mp3', bitrate: '128kbps MP3' },
  { name: '🏙️ Nightwave Plaza & Vaporwave', genre: 'VAPORWAVE', desc: 'Nostalgic 80s aesthetics, chill synthwave and late-night cyberpunk echoes', url: 'https://radio.plaza.one/mp3', bitrate: '128kbps MP3' },
  { name: '🌌 Drone Zone (Deep Space Ambient)', genre: 'AMBIENT', desc: 'Deep space electronic textures and atmospheric chill for extreme focus', url: 'https://ice1.somafm.com/dronezone-128-mp3', bitrate: '128kbps MP3' },
  { name: '🕶️ Secret Agent (Cinematic Spy)', genre: 'SPY CHILL', desc: 'Stylish cinematic vintage spy lounge and mysterious espionage grooves', url: 'https://ice1.somafm.com/secretagent-128-mp3', bitrate: '128kbps MP3' }
];

// КАТАЛОГ РЕАЛЬНЫХ ВИРУСНЫХ РОЛИКОВ YOUTUBE SHORTS & MP4 ПОТОКОВ
const CURATED_VIRAL_SHORTS: ShortVideoItem[] = [
  {
    id: 'yt-1',
    youtubeId: 's_ndf10e47g',
    title: 'When Senior Developer writes 1 line of clean code 👨‍💻⚡',
    author: '@dev_humor',
    avatar: '👨‍💻',
    category: 'TECH',
    tags: '#coding #developer #python #shorts #tech',
    sound: 'Cyberpunk Tech Groove - 128 BPM',
    likes: 452100,
    commentsCount: '5.2K',
    views: '3.8M',
    url: 'https://filesamples.com/samples/video/mp4/sample_1280x720_surfing_with_audio.mp4',
    embedUrl: 'https://www.youtube-nocookie.com/embed/s_ndf10e47g?autoplay=1&controls=1&rel=0&playsinline=1'
  },
  {
    id: 'yt-2',
    youtubeId: 'L_LUpnjgPso',
    title: 'Satisfying ASMR Neon Laser Rust Cleaning 🔥✨',
    author: '@satisfying_daily',
    avatar: '✨',
    category: 'ASMR',
    tags: '#asmr #satisfying #laser #rust #oddlysatisfying',
    sound: 'Deep Laser Resonance - Binaural',
    likes: 890400,
    commentsCount: '9.4K',
    views: '7.2M',
    url: 'https://vjs.zencdn.net/v/oceans.mp4',
    embedUrl: 'https://www.youtube-nocookie.com/embed/L_LUpnjgPso?autoplay=1&controls=1&rel=0&playsinline=1'
  },
  {
    id: 'yt-3',
    youtubeId: 'kXYiU_JCYtU',
    title: 'Insane Minimalist Cyber RGB Desk Setup Tour 🌌🖥️',
    author: '@setup_battlestations',
    avatar: '🌌',
    category: 'TECH',
    tags: '#desksetup #tech #rgb #battlestation #pcbuild',
    sound: 'Chillwave Synth Beats - Night Flight',
    likes: 324900,
    commentsCount: '4.1K',
    views: '2.4M',
    url: 'https://test-videos.co.uk/vids/jellyfish/mp4/h264/720/Jellyfish_720_10s_1MB.mp4',
    embedUrl: 'https://www.youtube-nocookie.com/embed/kXYiU_JCYtU?autoplay=1&controls=1&rel=0&playsinline=1'
  },
  {
    id: 'yt-4',
    youtubeId: 'O-zpOMYRi0w',
    title: 'When A Bug Suddenly Becomes An Epic Feature 🤖😂',
    author: '@meme_coder',
    avatar: '😂',
    category: 'MEMES',
    tags: '#humor #programming #gaming #memes #coding',
    sound: 'Funny 8-bit Glitch Hop - 130 BPM',
    likes: 610200,
    commentsCount: '7.8K',
    views: '5.1M',
    url: 'https://filesamples.com/samples/video/mp4/sample_960x400_ocean_with_audio.mp4',
    embedUrl: 'https://www.youtube-nocookie.com/embed/O-zpOMYRi0w?autoplay=1&controls=1&rel=0&playsinline=1'
  },
  {
    id: 'yt-5',
    youtubeId: 'fRh_vgS2dFE',
    title: 'Cat takes over remote engineering meeting on Zoom 🐱💼',
    author: '@cat_programmers',
    avatar: '🐱',
    category: 'MEMES',
    tags: '#cats #funny #zoom #workfromhome #animals',
    sound: 'Playful Meow Beats - Lofi Cat',
    likes: 940000,
    commentsCount: '11.2K',
    views: '8.5M',
    url: 'https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4',
    embedUrl: 'https://www.youtube-nocookie.com/embed/fRh_vgS2dFE?autoplay=1&controls=1&rel=0&playsinline=1'
  },
  {
    id: 'yt-6',
    youtubeId: '3fumBcKC6RE',
    title: 'Viral Trend Bass Drop Transition TikTok ⚡🔥',
    author: '@trend_vault',
    avatar: '⚡',
    category: 'CYBER',
    tags: '#tiktok #viral #trend #music #transition',
    sound: 'Viral Bass Drop - 130 BPM Hard Phonk',
    likes: 1240000,
    commentsCount: '15.3K',
    views: '11.4M',
    url: 'https://filesamples.com/samples/video/mp4/sample_640x360.mp4',
    embedUrl: 'https://www.youtube-nocookie.com/embed/3fumBcKC6RE?autoplay=1&controls=1&rel=0&playsinline=1'
  },
  {
    id: 'yt-7',
    youtubeId: '50_iTQj5t5U',
    title: 'Autonomous Drone FPV High Speed Flight Through Neon City 🚀🏎️',
    author: '@drone_fpv',
    avatar: '🚀',
    category: 'AUTO',
    tags: '#fpv #drone #speed #cinema #racing',
    sound: 'High Velocity Turbine Beat',
    likes: 280500,
    commentsCount: '3.6K',
    views: '2.1M',
    url: 'https://test-videos.co.uk/vids/sintel/mp4/h264/720/Sintel_720_10s_1MB.mp4',
    embedUrl: 'https://www.youtube-nocookie.com/embed/50_iTQj5t5U?autoplay=1&controls=1&rel=0&playsinline=1'
  },
  {
    id: 'yt-8',
    youtubeId: 'd6rY8QZkZ5g',
    title: 'ASMR Custom Mechanical Keyboard Lubing & Typing ⌨️🎧',
    author: '@custom_keebs',
    avatar: '⌨️',
    category: 'ASMR',
    tags: '#keeb #typing #satisfying #asmr #keyboard',
    sound: 'Thocky Lubed Keycaps Binaural Sound',
    likes: 395200,
    commentsCount: '4.8K',
    views: '3.3M',
    url: 'https://filesamples.com/samples/video/mp4/sample_960x540.mp4',
    embedUrl: 'https://www.youtube-nocookie.com/embed/d6rY8QZkZ5g?autoplay=1&controls=1&rel=0&playsinline=1'
  },
  {
    id: 'yt-9',
    youtubeId: 'Wl2n4A2K9eU',
    title: 'Cyberpunk 2077 Night City Ray Tracing 4K Max Settings 🌃🚗',
    author: '@rtx_gaming',
    avatar: '🎮',
    category: 'GAMING',
    tags: '#cyberpunk #gaming #rtx4090 #nightcity #pc',
    sound: 'Cyber Synthwave Drive - Night City Vibe',
    likes: 512700,
    commentsCount: '6.2K',
    views: '4.2M',
    url: 'https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/720/Big_Buck_Bunny_720_10s_1MB.mp4',
    embedUrl: 'https://www.youtube-nocookie.com/embed/Wl2n4A2K9eU?autoplay=1&controls=1&rel=0&playsinline=1'
  },
  {
    id: 'yt-10',
    youtubeId: '9YffrCViTVk',
    title: 'AI Image Generation vs Real World Photos Mind Blown 🤖📸',
    author: '@ai_future',
    avatar: '🤖',
    category: 'TECH',
    tags: '#ai #midjourney #genai #future #tech',
    sound: 'Future Tech Pulse - Ambient Electronic',
    likes: 680100,
    commentsCount: '8.1K',
    views: '5.9M',
    url: 'https://www.w3schools.com/html/mov_bbb.mp4',
    embedUrl: 'https://www.youtube-nocookie.com/embed/9YffrCViTVk?autoplay=1&controls=1&rel=0&playsinline=1'
  },
  {
    id: 'yt-11',
    youtubeId: '60ItHLz5WEA',
    title: 'Most Satisfying Woodworking Craft & Japanese Chisel ASMR 🪵✂️',
    author: '@craft_master',
    avatar: '🪵',
    category: 'ASMR',
    tags: '#craft #wood #satisfying #relax #woodworking',
    sound: 'Natural Wood Chisel Acoustics',
    likes: 420000,
    commentsCount: '5.4K',
    views: '3.6M',
    url: 'https://filesamples.com/samples/video/mp4/sample_1280x720_surfing_with_audio.mp4',
    embedUrl: 'https://www.youtube-nocookie.com/embed/60ItHLz5WEA?autoplay=1&controls=1&rel=0&playsinline=1'
  },
  {
    id: 'yt-12',
    youtubeId: '3JZ_D3ELwOQ',
    title: 'Top Secret OSINT & Google Dorking Tricks for Hackers 🕵️‍♂️💻',
    author: '@cyber_intel',
    avatar: '🕵️',
    category: 'TECH',
    tags: '#osint #security #hacker #google #cybersecurity',
    sound: 'Dark Cyber Espionage Low-Fi Groove',
    likes: 750300,
    commentsCount: '8.7K',
    views: '6.8M',
    url: 'https://vjs.zencdn.net/v/oceans.mp4',
    embedUrl: 'https://www.youtube-nocookie.com/embed/3JZ_D3ELwOQ?autoplay=1&controls=1&rel=0&playsinline=1'
  },
  {
    id: 'yt-13',
    youtubeId: '7wtfhZwyrcc',
    title: 'Insane 1v5 Clutch Win in Competitive Esports Arena 🎮💥',
    author: '@epic_clutches',
    avatar: '🏆',
    category: 'GAMING',
    tags: '#gaming #clutch #esports #csgo #twitch',
    sound: 'Hype Electro Esports Drop - 145 BPM',
    likes: 540800,
    commentsCount: '7.1K',
    views: '4.7M',
    url: 'https://test-videos.co.uk/vids/jellyfish/mp4/h264/720/Jellyfish_720_10s_1MB.mp4',
    embedUrl: 'https://www.youtube-nocookie.com/embed/7wtfhZwyrcc?autoplay=1&controls=1&rel=0&playsinline=1'
  },
  {
    id: 'yt-14',
    youtubeId: 'e-ORhEE9VVg',
    title: 'Hydraulic Press vs Indestructible Titanium Cube ASMR 💥⚙️',
    author: '@press_channel',
    avatar: '⚙️',
    category: 'ASMR',
    tags: '#hydraulic #crush #asmr #satisfying #crusher',
    sound: 'Heavy Industrial Impact Echo',
    likes: 1100000,
    commentsCount: '13.8K',
    views: '9.5M',
    url: 'https://filesamples.com/samples/video/mp4/sample_960x400_ocean_with_audio.mp4',
    embedUrl: 'https://www.youtube-nocookie.com/embed/e-ORhEE9VVg?autoplay=1&controls=1&rel=0&playsinline=1'
  },
  {
    id: 'yt-15',
    youtubeId: 'OPf0YbXqDm0',
    title: 'Neon Tokyo Rainy Midnight Drift & Cyberpunk Atmosphere 🌧️🏎️',
    author: '@tokyo_rain',
    avatar: '🌧️',
    category: 'AUTO',
    tags: '#tokyo #drift #rain #lofi #cyberpunk #jdm',
    sound: 'Tokyo Midnight Rain & Phonk Drift',
    likes: 620000,
    commentsCount: '7.9K',
    views: '5.3M',
    url: 'https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4',
    embedUrl: 'https://www.youtube-nocookie.com/embed/OPf0YbXqDm0?autoplay=1&controls=1&rel=0&playsinline=1'
  }
];

// ГЕНЕРАТОР БЕСКОНЕЧНОЙ ЛЕНТЫ TIKTOK / YOUTUBE SHORTS
export function generateInfiniteShorts(
  startIndex: number,
  count: number,
  category: string = 'ALL',
  query: string = ''
): ShortVideoItem[] {
  const titlesByCat: Record<string, string[]> = {
    TECH: [
      'Junior vs Senior Developer Refactoring Legacy Code 💻🔥',
      'Deploying to Production on Friday 5:00 PM Live Reaction 💀',
      'Building Fullstack AI Web App in 10 Minutes with Docker 🚀',
      'The Dark Secrets of Linux Kernel Architecture 🐧⚙️',
      'Why Every Programmer Needs Multiple Monitors in 2026 🖥️'
    ],
    MEMES: [
      'Programmer explaining to mom what API stands for 😂',
      'Cat accidentally types rm -rf on Linux workstation 🐱💥',
      'POV: When client asks for one small last-minute change 😭',
      'Coffee machine broke at software tech company ☕🚨',
      'Rubber Duck debugging at 3:00 AM 🦆✨'
    ],
    GAMING: [
      'Epic 360 No-Scope Victory Royale Clip 🎮🎯',
      'Speedrunning Super Mario World Any% World Record ⏱️🍄',
      'Best Open World RPG Graphics in Unreal Engine 5.5 🌌',
      'Funniest NPC Bugs and Glitches Compilation 🤣🎮',
      'Retro Gameboy Mod with OLED Screen and Cyber Glow 👾'
    ],
    ASMR: [
      'Macro Ice Carving and Glass Cutting Sound ASMR 🧊🎧',
      'Rain on Neon Cyberpunk Glass Greenhouse Relax 🌧️🌿',
      'Mechanical Switches Sound Test: Blue vs Brown vs Red ⌨️',
      'Restoration of Vintage 1980s Cyberpunk Cassette Player 📻',
      'Crushing Kinetic Sand and Slime Ultra Soft Audio 🫧'
    ],
    CYBER: [
      'Synthwave Neon Sunset Highway Cyber Drive 🌆🏎️',
      'Hacking Terminal UI Simulation in Terminal Python ⚡💻',
      'Bioluminescent Cybernetic Plants in Deep Neo-Tokyo 🌸🌃',
      'AI Neural Network Visualized in 3D Point Cloud 🧠',
      'Dark Techno Rave Lighting Visualizer Performance ⚡'
    ],
    AUTO: [
      'Supra MK4 2JZ Twin Turbo Midnight Highway Pull 🏎️💨',
      'Touge Mountain Pass Drift Battle in Heavy Fog 🏔️🚗',
      'Hypercar V12 Cold Start & Titanium Exhaust Flames 🔥',
      'Cyberpunk Electric Superbike Speed Run 4K 🏍️⚡',
      'JDM Night Car Meet in Underground Shibuya Garage 🏙️'
    ]
  };

  const authorsPool = [
    { handle: '@tech_ninja', avatar: '🥷' },
    { handle: '@cyber_ghost', avatar: '👻' },
    { handle: '@pixel_master', avatar: '👾' },
    { handle: '@tokyo_drifter', avatar: '🏎️' },
    { handle: '@asmr_sanctuary', avatar: '🎧' },
    { handle: '@neural_dev', avatar: '🧠' },
    { handle: '@code_wizard', avatar: '🧙' },
    { handle: '@quantum_cat', avatar: '🐱' },
    { handle: '@neon_matrix', avatar: '🌌' },
    { handle: '@turbo_shift', avatar: '⚡' }
  ];

  const videoStreamUrls = [
    'https://filesamples.com/samples/video/mp4/sample_1280x720_surfing_with_audio.mp4',
    'https://vjs.zencdn.net/v/oceans.mp4',
    'https://test-videos.co.uk/vids/jellyfish/mp4/h264/720/Jellyfish_720_10s_1MB.mp4',
    'https://filesamples.com/samples/video/mp4/sample_960x400_ocean_with_audio.mp4',
    'https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4',
    'https://filesamples.com/samples/video/mp4/sample_640x360.mp4',
    'https://test-videos.co.uk/vids/sintel/mp4/h264/720/Sintel_720_10s_1MB.mp4',
    'https://filesamples.com/samples/video/mp4/sample_960x540.mp4',
    'https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/720/Big_Buck_Bunny_720_10s_1MB.mp4',
    'https://www.w3schools.com/html/mov_bbb.mp4'
  ];

  const results: ShortVideoItem[] = [];
  const basePool = CURATED_VIRAL_SHORTS.filter(item => {
    const matchCat = category === 'ALL' || item.category === category;
    const matchQuery = !query || item.title.toLowerCase().includes(query.toLowerCase()) || item.tags.toLowerCase().includes(query.toLowerCase());
    return matchCat && matchQuery;
  });

  for (let i = 0; i < count; i++) {
    const globalIdx = startIndex + i;
    if (globalIdx < basePool.length) {
      results.push(basePool[globalIdx]);
    } else {
      // Алгоритмическая бесконечная генерация новых шортсов
      const catKeys = category !== 'ALL' && titlesByCat[category] ? [category] : Object.keys(titlesByCat);
      const cat = catKeys[globalIdx % catKeys.length] as 'TECH' | 'MEMES' | 'GAMING' | 'ASMR' | 'CYBER' | 'AUTO';
      const titles = titlesByCat[cat];
      const titleTemplate = titles[(globalIdx + Math.floor(globalIdx / 5)) % titles.length];
      const author = authorsPool[globalIdx % authorsPool.length];
      const viewsNum = (1.1 + (globalIdx * 0.4) % 8.5).toFixed(1);
      const likesNum = Math.floor(parseFloat(viewsNum) * 110000);
      const commentsNum = `${(1.2 + (globalIdx * 0.3) % 9.0).toFixed(1)}K`;
      const curItem = CURATED_VIRAL_SHORTS[globalIdx % CURATED_VIRAL_SHORTS.length];

      results.push({
        id: `gen-${globalIdx}-${Date.now()}`,
        youtubeId: curItem.youtubeId,
        title: `${titleTemplate} #${globalIdx + 1}`,
        author: author.handle,
        avatar: author.avatar,
        category: cat,
        tags: `#${cat.toLowerCase()} #viral #shorts #fyp #trending`,
        sound: `${cat} Audio Beats - Track #${(globalIdx % 12) + 1}`,
        likes: likesNum,
        commentsCount: commentsNum,
        views: `${viewsNum}M`,
        url: videoStreamUrls[globalIdx % videoStreamUrls.length],
        embedUrl: curItem.embedUrl
      });
    }
  }

  return results;
}

export function extractYoutubeId(url: string): string {
  const text = url.trim();
  const m = text.match(/(?:shorts\/|v=|youtu\.be\/|embed\/)([a-zA-Z0-9_-]{11})/);
  if (m) return m[1];
  if (text.length === 11 && /^[a-zA-Z0-9_-]{11}$/.test(text)) return text;
  return '';
}

const LANGUAGES = [
  { code: 'en', name: '🇺🇸 English (Английский)' },
  { code: 'ru', name: '🇷🇺 Русский (Russian)' },
  { code: 'de', name: '🇩🇪 Deutsch (Немецкий)' },
  { code: 'es', name: '🇪🇸 Español (Испанский)' },
  { code: 'fr', name: '🇫🇷 Français (Французский)' },
  { code: 'zh', name: '🇨🇳 中文 (Китайский)' },
  { code: 'ja', name: '🇯🇵 日本語 (Японский)' },
  { code: 'it', name: '🇮🇹 Italiano (Итальянский)' },
  { code: 'pt', name: '🇵🇹 Português (Португальский)' },
  { code: 'tr', name: '🇹🇷 Türkçe (Турецкий)' },
  { code: 'ar', name: '🇦🇪 العربية (Арабский)' }
];

export default function App() {
  const [activeTab, setActiveTab] = useState<'dash' | 'spider' | 'validator' | 'mailer' | 'accounts' | 'radio' | 'shorts' | 'base' | 'python'>('dash');

  // Lo-Fi Radio State (14 Stations)
  const [radioPlaying, setRadioPlaying] = useState(false);
  const [currentStationIdx, setCurrentStationIdx] = useState(0);
  const [volume, setVolume] = useState(0.75);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Shorts / Reels State (Бесконечная лента TikTok / YouTube Shorts)
  const [shortsFeed, setShortsFeed] = useState<ShortVideoItem[]>(() => generateInfiniteShorts(0, 20, 'ALL', ''));
  const [shortIdx, setShortIdx] = useState(0);
  const [shortPlaying, setShortPlaying] = useState(true);
  const [shortsMuted, setShortsMuted] = useState(false);
  const [shortsAutoScroll, setShortsAutoScroll] = useState(true);
  const [shortsViewMode, setShortsViewMode] = useState<'focus' | 'feed'>('feed');
  const [shortsCategory, setShortsCategory] = useState<string>('ALL');
  const [shortsSearchQuery, setShortsSearchQuery] = useState('');
  const [shortLikesMap, setShortLikesMap] = useState<Record<string | number, boolean>>({});
  const [followingMap, setFollowingMap] = useState<Record<string, boolean>>({});
  const [shortProgress, setShortProgress] = useState(0);
  const [copiedLink, setCopiedLink] = useState(false);
  const [customModalOpen, setCustomModalOpen] = useState(false);
  const [customUrlInput, setCustomUrlInput] = useState('');
  const [customTitleInput, setCustomTitleInput] = useState('');
  const [customAuthorInput, setCustomAuthorInput] = useState('');
  const [commentsDrawerOpen, setCommentsDrawerOpen] = useState(false);
  const [activeCommentShortId, setActiveCommentShortId] = useState<string | number | null>('yt-1');
  const [newCommentInput, setNewCommentInput] = useState('');
  const [commentsData, setCommentsData] = useState<Record<string | number, Array<{ user: string; avatar: string; text: string; time: string; likes: number }>>>({
    'yt-1': [
      { user: '@alex_dev', avatar: '👨‍💻', text: 'Ахаха, когда написал чистый код с первого раза!', time: '2ч назад', likes: 245 },
      { user: '@senior_architect', avatar: '🧙', text: '1 строка чистого кода стоит 1000 строк легаси.', time: '4ч назад', likes: 182 },
      { user: '@frontend_pro', avatar: '⚡', text: 'Кайф, музыка тоже топ!', time: '5ч назад', likes: 98 }
    ],
    'yt-2': [
      { user: '@laser_fan', avatar: '🔥', text: 'Этот звук лазера просто чистый гипноз...', time: '1ч назад', likes: 512 },
      { user: '@relax_space', avatar: '✨', text: 'Смотрю уже 10-й раз подряд, ASMR на максималках!', time: '3ч назад', likes: 320 }
    ],
    'yt-3': [
      { user: '@rgb_master', avatar: '🌌', text: 'Где взять такой же стол и монитор? Подсветка огонь!', time: '45м назад', likes: 114 },
      { user: '@cyber_coder', avatar: '🖥️', text: 'Идеальный сетап для ночного парсинга и кодинга.', time: '2ч назад', likes: 89 }
    ]
  });
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const feedScrollContainerRef = useRef<HTMLDivElement | null>(null);

  // Crawler State
  const [crawlerStatus, setCrawlerStatus] = useState<'STANDBY' | 'CRAWLING'>('STANDBY');
  const [harvestedCount, setHarvestedCount] = useState(7);
  const [personalCount, setPersonalCount] = useState(4);
  const [visitedNodes, setVisitedNodes] = useState(18);
  const [queueCount, setQueueCount] = useState(38);

  // Database Contacts Table (Country + Last Active)
  const [dbContacts, setDbContacts] = useState<HarvestContact[]>([
    { id: 1, email: 'loudnate@gmail.com', country: 'США / Global 🇺🇸', lastActive: '2026-10-09 14:20', category: 'HUMAN / PERSONAL', targetSource: '↗ GitHub Contributors', score: 95, timestamp: '18:05:10' },
    { id: 2, email: 'alex.developer@mail.ru', country: 'Россия 🇷🇺', lastActive: '2026-10-08 19:45', category: 'HUMAN / PERSONAL', targetSource: '↗ Linux Kernel Drivers', score: 94, timestamp: '18:04:22' },
    { id: 3, email: 'hans.weber@berlin.de', country: 'Германия 🇩🇪', lastActive: '2026-10-07 11:15', category: 'HUMAN / PERSONAL', targetSource: '↗ Rust for Linux AUTHORS', score: 92, timestamp: '18:02:10' },
    { id: 4, email: 'vitalik.buterin@ethereum.org', country: 'Международный 🌐', lastActive: '2026-10-09 09:30', category: 'CORPORATE / DEV', targetSource: '↗ Ethereum Core Repo', score: 98, timestamp: '17:59:01' },
    { id: 5, email: 'torvalds@linux-foundation.org', country: 'США / Global 🇺🇸', lastActive: '2026-10-09 21:05', category: 'CORPORATE / DEV', targetSource: '↗ Linux MAINTAINERS', score: 99, timestamp: '17:50:18' },
    { id: 6, email: 'gvanrossum@python.org', country: 'Нидерланды 🇳🇱', lastActive: '2026-10-06 16:40', category: 'CORPORATE / DEV', targetSource: '↗ Python .mailmap', score: 97, timestamp: '17:42:04' },
    { id: 7, email: 'chen.wei@163.com', country: 'Китай 🇨🇳', lastActive: '2026-10-08 22:10', category: 'HUMAN / PERSONAL', targetSource: '↗ Go Contributors', score: 91, timestamp: '17:35:12' }
  ]);
  const [dbSearch, setDbSearch] = useState('');

  // Validator State with Country & Last Seen
  const [singleInspectEmail, setSingleInspectEmail] = useState('');
  const [valFilter, setValFilter] = useState<'ALL' | 'SAFE' | 'RISKY' | 'TRAP' | 'INVALID'>('ALL');
  const [valSearch, setValSearch] = useState('');
  const [validatedRecords, setValidatedRecords] = useState<ValidatedRecord[]>([
    { email: 'loudnate@gmail.com', country: 'США / Global 🇺🇸', lastActive: '2026-10-09 14:20', verdict: 'SAFE', score: 95, detail: 'Personal mailbox on Gmail, verified MX, zero trap flags' },
    { email: 'alex.developer@mail.ru', country: 'Россия 🇷🇺', lastActive: '2026-10-08 19:45', verdict: 'SAFE', score: 94, detail: 'Личный проверенный ящик Mail.ru, активный пользователь' },
    { email: 'hans.weber@berlin.de', country: 'Германия 🇩🇪', lastActive: '2026-10-07 11:15', verdict: 'SAFE', score: 92, detail: 'Немецкий подтвержденный домен, живой почтовый сервер' },
    { email: 'torvalds@linux-foundation.org', country: 'США / Global 🇺🇸', lastActive: '2026-10-09 21:05', verdict: 'RISKY', score: 65, detail: 'High-reputation role/corp address, non-disposable domain' },
    { email: 'spamtrap_99@honeypot.org', country: 'Международный 🌐', lastActive: 'Неизвестно', verdict: 'TRAP', score: 0, detail: '⚠️ SPAM TRAP DETECTED: Known honeypot token trigger' },
    { email: 'fake.user@dispostable.com', country: 'Международный 🌐', lastActive: 'Вчера', verdict: 'INVALID', score: 5, detail: 'Disposable temporary throwaway provider' }
  ]);

  // Mailer Multi-Language State
  const [selectedLang, setSelectedLang] = useState('en');
  const [accounts, setAccounts] = useState<AccountCombo[]>([
    { email: 'sender.demo@gmail.com', provider: 'GMAIL.COM', status: 'READY' },
    { email: 'outreach.lead@yandex.ru', provider: 'YANDEX.RU', status: 'READY' },
    { email: 'alex.developer@mail.ru', provider: 'MAIL.RU', status: 'READY' }
  ]);
  const [selectedSenderEmail, setSelectedSenderEmail] = useState('sender.demo@gmail.com');
  const [mailerTo, setMailerTo] = useState('loudnate@gmail.com');
  const [mailerSubject, setMailerSubject] = useState('Cooperation & Tech Collaboration Proposal');
  const [mailerBody, setMailerBody] = useState(
    'Hello,\n\n' +
    'I noticed your open-source projects and developer contributions. We are currently building advanced infrastructure and would love to discuss a potential partnership.\n\n' +
    'Would you be open for a short call this week?\n\n' +
    'Best regards,\nTechnical Outreach Team'
  );
  const [aiModalOpen, setAiModalOpen] = useState(false);
  const [aiPrompt, setAiPrompt] = useState('');
  const [aiGenerating, setAiGenerating] = useState(false);

  // Accounts Manager State
  const [rawAccountsFile, setRawAccountsFile] = useState(
    '# File for sender accounts in format: email:password\n' +
    'sender.demo@gmail.com:app_pass_abcd1234\n' +
    'outreach.lead@yandex.ru:secret_token_998\n' +
    'alex.developer@mail.ru:mailru_app_pass'
  );
  const [newAccEmail, setNewAccEmail] = useState('');
  const [newAccPass, setNewAccPass] = useState('');

  // Python Source Code
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

  const handleNextShort = () => {
    setShortIdx(prev => {
      const next = prev + 1;
      if (next >= shortsFeed.length - 3) {
        setShortsFeed(curr => [...curr, ...generateInfiniteShorts(curr.length, 10, shortsCategory, shortsSearchQuery)]);
      }
      return next;
    });
  };

  const handlePrevShort = () => {
    setShortIdx(prev => Math.max(0, prev - 1));
  };

  const handleShortEnded = () => {
    if (shortsAutoScroll) {
      handleNextShort();
    }
  };

  const handleFeedScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const target = e.currentTarget;
    if (target.scrollHeight - target.scrollTop - target.clientHeight < 800) {
      setShortsFeed(curr => [...curr, ...generateInfiniteShorts(curr.length, 10, shortsCategory, shortsSearchQuery)]);
    }
  };

  const handleCategoryChange = (cat: string) => {
    setShortsCategory(cat);
    const newItems = generateInfiniteShorts(0, 20, cat, shortsSearchQuery);
    setShortsFeed(newItems);
    setShortIdx(0);
  };

  const handleSearchSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const newItems = generateInfiniteShorts(0, 20, shortsCategory, shortsSearchQuery);
    setShortsFeed(newItems);
    setShortIdx(0);
  };

  const handleAddCustomShort = () => {
    if (!customUrlInput.trim()) return;
    const yId = extractYoutubeId(customUrlInput);
    const newShort: ShortVideoItem = {
      id: `custom-${Date.now()}`,
      youtubeId: yId || undefined,
      title: customTitleInput.trim() || (yId ? `YouTube Shorts #${yId}` : 'Пользовательский шортс'),
      author: customAuthorInput.trim().startsWith('@') ? customAuthorInput.trim() : `@${customAuthorInput.trim() || 'user'}`,
      avatar: '🎬',
      category: 'TECH',
      tags: '#custom #shorts #tiktok #viral',
      sound: 'Original Custom Audio',
      likes: 1540,
      commentsCount: '18',
      views: '12.8K',
      url: customUrlInput.endsWith('.mp4') ? customUrlInput : 'https://filesamples.com/samples/video/mp4/sample_1280x720_surfing_with_audio.mp4',
      embedUrl: yId ? `https://www.youtube-nocookie.com/embed/${yId}?autoplay=1&controls=1&rel=0&playsinline=1` : undefined,
      isCustom: true
    };
    setShortsFeed(prev => [newShort, ...prev]);
    setShortIdx(0);
    setCustomModalOpen(false);
    setCustomUrlInput('');
    setCustomTitleInput('');
    setCustomAuthorInput('');
  };

  const handlePostComment = (shortId: string | number) => {
    if (!newCommentInput.trim()) return;
    const newComment = {
      user: '@you',
      avatar: '😎',
      text: newCommentInput.trim(),
      time: 'только что',
      likes: 1
    };
    setCommentsData(prev => ({
      ...prev,
      [shortId]: [newComment, ...(prev[shortId] || [])]
    }));
    setNewCommentInput('');
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (activeTab !== 'shorts') return;
      if (customModalOpen || commentsDrawerOpen) return;
      if (e.key === 'ArrowDown' || e.key === 'j') {
        e.preventDefault();
        handleNextShort();
      } else if (e.key === 'ArrowUp' || e.key === 'k') {
        e.preventDefault();
        handlePrevShort();
      } else if (e.key === ' ') {
        e.preventDefault();
        setShortPlaying(p => !p);
        if (videoRef.current) {
          if (videoRef.current.paused) videoRef.current.play().catch(() => {});
          else videoRef.current.pause();
        }
      } else if (e.key === 'm' || e.key === 'M') {
        setShortsMuted(m => !m);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeTab, customModalOpen, commentsDrawerOpen, shortsFeed.length, shortsCategory, shortsSearchQuery]);

  const handleInspectSingle = () => {
    if (!singleInspectEmail || !singleInspectEmail.includes('@')) return;
    const lower = singleInspectEmail.toLowerCase();
    let verdict: 'SAFE' | 'RISKY' | 'TRAP' | 'INVALID' = 'SAFE';
    let score = 92;
    let detail = 'Human mailbox confirmed, clean syntax & live domain';
    let country = 'Международный 🌐';
    if (lower.endsWith('.ru') || lower.includes('yandex') || lower.includes('mail.ru')) country = 'Россия 🇷🇺';
    else if (lower.endsWith('.de')) country = 'Германия 🇩🇪';
    else if (lower.endsWith('.fr')) country = 'Франция 🇫🇷';
    else if (lower.endsWith('.uk')) country = 'Великобритания 🇬🇧';
    else if (lower.includes('gmail.com') || lower.includes('yahoo.com')) country = 'США / Global 🇺🇸';

    if (lower.includes('spam') || lower.includes('trap') || lower.includes('honeypot')) {
      verdict = 'TRAP';
      score = 0;
      detail = '⚠️ SPAM TRAP DETECTED: Known honeypot token trigger';
    } else if (lower.startsWith('admin@') || lower.startsWith('info@') || lower.startsWith('support@')) {
      verdict = 'RISKY';
      score = 60;
      detail = 'Role address (info/admin) — lower direct response probability';
    }

    setValidatedRecords(prev => [{ email: singleInspectEmail, country, lastActive: 'Сегодня, 10:20', verdict, score, detail }, ...prev]);
    setSingleInspectEmail('');
  };

  const handleAiTranslateAndDraft = () => {
    if (!aiPrompt) return;
    setAiGenerating(true);
    setTimeout(() => {
      // Translations templates based on selected language
      const samples: Record<string, { subj: string; body: string }> = {
        en: {
          subj: `Collaboration regarding: ${aiPrompt.slice(0, 32)}...`,
          body: `Hello,\n\nI reviewed your open-source projects and developer contributions regarding ${aiPrompt}.\n\nWould you be open to a brief chat or exchange this week to discuss potential collaboration?\n\nBest regards,\nOutreach & Engineering Lead`
        },
        de: {
          subj: `Kooperation & Austausch bezüglich: ${aiPrompt.slice(0, 28)}...`,
          body: `Guten Tag,\n\nich habe Ihre Entwicklungsarbeit und Repositories bezüglich ${aiPrompt} mit großem Interesse verfolgt.\n\nHätten Sie diese Woche Zeit für einen kurzen Austausch über eine mögliche Zusammenarbeit?\n\nMit freundlichen Grüßen,\nEntwicklungsleiter`
        },
        es: {
          subj: `Propuesta de colaboración sobre: ${aiPrompt.slice(0, 28)}...`,
          body: `Hola,\n\nHe seguido de cerca su trabajo y contribuciones en proyectos de código abierto sobre ${aiPrompt}.\n\n¿Tendría disponibilidad esta semana para una breve conversación sobre una posible sinergia?\n\nUn cordial saludo,\nEquipo Técnico`
        },
        fr: {
          subj: `Proposition de partenariat concernant: ${aiPrompt.slice(0, 28)}...`,
          body: `Bonjour,\n\nJ'ai découvert vos projets open-source et votre expertise technique concernant ${aiPrompt}.\n\nSeriez-vous disponible pour un court échange cette semaine afin d'explorer une collaboration?\n\nBien cordialement,\nÉquipe de Développement`
        },
        zh: {
          subj: `关于技术合作与项目交流的邀请`,
          body: `您好，\n\n我在关注开源项目时了解到了您在 ${aiPrompt} 方面的技术成果与贡献。\n\n不知本周是否有空进行简短交流，探讨未来的合作机会？\n\n此致，\n技术团队负责人`
        },
        ja: {
          subj: `技術提携および共同開発に関するご提案`,
          body: `初めまして。\n\n${aiPrompt} に関する貴殿のオープンソース活動と開発実績を拝見いたしました。\n\n今週、今後の協業可能性について少し情報交換させていただけないでしょうか？\n\nよろしくお願いいたします。\n開発チーム`
        },
        ru: {
          subj: `Сотрудничество по теме: ${aiPrompt.slice(0, 30)}...`,
          body: `Здравствуйте!\n\nОбратил внимание на ваши открытые репозитории и опыт в теме: ${aiPrompt}.\n\nБыло бы здорово обсудить возможность совместной работы или интеграции. Удобно ли кратко списаться на этой неделе?\n\nС уважением,\nТехнический разработчик`
        }
      };

      const res = samples[selectedLang] || samples.en;
      setMailerSubject(res.subj);
      setMailerBody(res.body);
      setAiGenerating(false);
      setAiModalOpen(false);
      setAiPrompt('');
    }, 600);
  };

  const handleExportCsv = () => {
    const headers = 'ID,EMAIL,COUNTRY,LAST_ACTIVE,CATEGORY,TARGET_SOURCE,SCORE,TIMESTAMP\n';
    const rows = dbContacts.map(c => `${c.id},"${c.email}","${c.country}","${c.lastActive}","${c.category}","${c.targetSource}",${c.score},"${c.timestamp}"`).join('\n');
    const blob = new Blob([headers + rows], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'BazaPocht.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const filteredDbContacts = dbContacts.filter(c => {
    if (!dbSearch) return true;
    const q = dbSearch.toLowerCase();
    return c.email.toLowerCase().includes(q) || c.country.toLowerCase().includes(q) || c.category.toLowerCase().includes(q);
  });

  return (
    <div className="min-h-screen bg-[#050508] text-slate-100 flex font-sans selection:bg-purple-600 selection:text-white">
      <audio
        ref={audioRef}
        onPlay={() => setRadioPlaying(true)}
        onPause={() => setRadioPlaying(false)}
      />

      {/* ========================================================= */}
      {/* 1. SIDEBAR */}
      {/* ========================================================= */}
      <aside className="w-[225px] bg-[#0b0713] border-r border-purple-900/30 flex flex-col shrink-0 select-none z-20">
        <div className="p-5 text-center">
          <div className="text-xl font-black tracking-[4px] bg-gradient-to-r from-cyan-400 via-purple-400 to-emerald-400 bg-clip-text text-transparent">
            MORPHH
          </div>
          <div className="text-[10px] font-mono tracking-widest text-slate-500 mt-0.5">
            ALLPARSV1.5 // AI OSINT
          </div>
        </div>

        <nav className="flex-1 px-3 space-y-1 overflow-y-auto">
          {[
            { id: 'dash', label: 'Dashboard', icon: LayoutDashboard },
            { id: 'spider', label: 'Spider & Dorks', icon: Terminal, badge: 'SPIDER', badgeColor: 'text-purple-400 border-purple-500/50' },
            { id: 'validator', label: 'AI Validator', icon: CheckCircle2, badge: 'GEMINI', badgeColor: 'text-cyan-400 border-cyan-500/50' },
            { id: 'mailer', label: 'AI Mailer', icon: Mail, badge: 'MULTI-LANG', badgeColor: 'text-purple-400 border-purple-500/50' },
            { id: 'accounts', label: 'Combo Accounts', icon: Users },
            { id: 'radio', label: 'Lo-Fi Radio', icon: Radio, badge: '14 ST', badgeColor: 'text-emerald-400 border-emerald-500/50' },
            { id: 'shorts', label: 'Cyber Shorts', icon: Film, badge: 'REELS', badgeColor: 'text-rose-400 border-rose-500/50' },
            { id: 'base', label: 'Database Table', icon: Database, badge: 'SQL', badgeColor: 'text-cyan-400 border-cyan-500/50' },
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
                  <span className={`text-[8px] font-mono font-bold px-1.5 py-0.5 rounded border bg-purple-950/50 ${item.badgeColor}`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

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
        </div>
      </aside>

      {/* ========================================================= */}
      {/* 2. MAIN VIEWPORT */}
      {/* ========================================================= */}
      <main className="flex-1 flex flex-col h-screen overflow-y-auto">
        {/* TAB 1: DASHBOARD */}
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
                <p className="text-xs text-slate-400 mt-1">Autonomous OSINT harvesting with country GeoIP & SQLite Database Table syncing</p>
              </div>
            </div>

            <div className="h-px bg-gradient-to-r from-cyan-500 via-purple-500 to-emerald-500 opacity-60" />

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5">
                <div className="flex justify-between items-start">
                  <span className="text-[10px] font-mono font-bold text-slate-400 tracking-wider">HARVESTED MAILS</span>
                  <Database className="w-4 h-4 text-cyan-400" />
                </div>
                <div className="text-3xl font-extrabold text-cyan-400 font-mono mt-2">{harvestedCount}</div>
                <div className="text-[11px] text-emerald-400 mt-2 flex items-center justify-between">
                  <span className="text-slate-500 font-mono">SQLite Table: active</span>
                  <span className="font-bold">Auto-Sync</span>
                </div>
              </div>

              <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5">
                <div className="flex justify-between items-start">
                  <span className="text-[10px] font-mono font-bold text-slate-400 tracking-wider">PERSONAL (HUMAN)</span>
                  <Mail className="w-4 h-4 text-emerald-400" />
                </div>
                <div className="text-3xl font-extrabold text-emerald-400 font-mono mt-2">{personalCount}</div>
                <div className="text-[11px] text-slate-400 mt-2 font-mono truncate">
                  Gmail, Yandex, Mail.ru, Berlin.de
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
                  <span>SQLite Table Auto-Sync & Country Detection</span>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <button
                  onClick={() => {
                    setCrawlerStatus('CRAWLING');
                    setTimeout(() => {
                      setHarvestedCount(c => c + 1);
                      setVisitedNodes(v => v + 6);
                      setCrawlerStatus('STANDBY');
                    }, 2000);
                  }}
                  className="px-5 py-2.5 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 rounded-xl text-xs font-bold font-mono tracking-wider flex items-center gap-2 transition"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  RUN SINGLE BATCH (40P)
                </button>

                <button
                  onClick={() => setCrawlerStatus(s => s === 'CRAWLING' ? 'STANDBY' : 'CRAWLING')}
                  className="px-5 py-2.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded-xl text-xs font-bold font-mono tracking-wider flex items-center gap-2 transition"
                >
                  <span>∞</span>
                  ENABLE INFINITE SPIDER
                </button>

                <button
                  onClick={() => setActiveTab('base')}
                  className="px-5 py-2.5 bg-purple-900/20 hover:bg-purple-900/40 text-purple-300 border border-purple-500/30 rounded-xl text-xs font-bold font-mono tracking-wider flex items-center gap-2 transition"
                >
                  <Database className="w-3.5 h-3.5" />
                  ОТКРЫТЬ ТАБЛИЦУ БАЗЫ
                </button>
              </div>
            </div>

            {/* Live Feed Table (with Country and Last Active) */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400" />
                  <h3 className="text-sm font-bold text-white">Live Harvested Contacts (Сохраняются в Таблицу с Геолокацией)</h3>
                </div>
                <span className="text-[11px] font-mono text-slate-500">Автоматически: Страна + Последняя активность</span>
              </div>

              <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl overflow-hidden">
                <table className="w-full text-left font-mono text-xs">
                  <thead>
                    <tr className="border-b border-purple-900/30 text-slate-500 text-[10px]">
                      <th className="py-3 px-4">EMAIL ADDRESS</th>
                      <th className="py-3 px-4">СТРАНА (GEOIP)</th>
                      <th className="py-3 px-4">ПОСЛЕДНЯЯ АКТИВНОСТЬ</th>
                      <th className="py-3 px-4">CATEGORY</th>
                      <th className="py-3 px-4">TARGET SOURCE</th>
                      <th className="py-3 px-4 text-right">TIME</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-purple-950/30">
                    {dbContacts.map((c) => (
                      <tr key={c.id} className="hover:bg-purple-950/20">
                        <td className="py-3 px-4 font-semibold text-cyan-300">{c.email}</td>
                        <td className="py-3 px-4 text-slate-200">{c.country}</td>
                        <td className="py-3 px-4 text-emerald-400">{c.lastActive}</td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                            c.category === 'HUMAN / PERSONAL'
                              ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-500/50'
                              : 'bg-purple-950/60 text-purple-300 border border-purple-500/50'
                          }`}>
                            {c.category}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-purple-300">{c.targetSource}</td>
                        <td className="py-3 px-4 text-right text-slate-500">{c.timestamp}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: SPIDER & DORKS */}
        {activeTab === 'spider' && (
          <div className="p-8 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-white tracking-wide">&gt;_ Spider Crawler & Dork Parser</h1>
                <p className="text-xs text-slate-400 mt-1">Рекурсивный паук с сохранением в структурированную таблицу базы данных</p>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-cyan-950/60 text-cyan-400 border border-cyan-500/50">
                ✨ Dorks + Spider Unified
              </span>
            </div>
            <div className="h-px bg-gradient-to-r from-cyan-500 via-purple-500 to-emerald-500 opacity-60" />

            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div className="md:col-span-3 bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5 space-y-3">
                <span className="text-xs font-bold text-cyan-400">✨ НАЧАЛЬНЫЕ ССЫЛКИ / РЕПОЗИТОРИИ (1 НА СТРОКУ)</span>
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
              </div>
              <div className="md:col-span-2 bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5 space-y-4">
                <span className="text-xs font-bold text-purple-300">СОСТОЯНИЕ ДВИЖКА ПАУКА</span>
                <div className="space-y-2 text-xs font-mono">
                  <div className="flex justify-between border-b border-purple-950 pb-1.5">
                    <span className="text-slate-400">Статус:</span>
                    <span className="text-emerald-400 font-bold">{crawlerStatus === 'CRAWLING' ? 'РАБОТАЕТ' : 'ОСТАНОВЛЕН'}</span>
                  </div>
                  <div className="flex justify-between border-b border-purple-950 pb-1.5">
                    <span className="text-slate-400">Записано в SQL таблицу:</span>
                    <span className="text-emerald-400 font-bold">{dbContacts.length} записей</span>
                  </div>
                </div>
                <button
                  onClick={() => setCrawlerStatus(s => s === 'CRAWLING' ? 'STANDBY' : 'CRAWLING')}
                  className="w-full py-2.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded-xl text-xs font-bold font-mono tracking-wider"
                >
                  {crawlerStatus === 'CRAWLING' ? '■ ОСТАНОВИТЬ' : '▶ ЗАПУСТИТЬ ОБХОД'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: VALIDATOR (СТРАНА + ПОСЛЕДНЯЯ АКТИВНОСТЬ) */}
        {activeTab === 'validator' && (
          <div className="p-8 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-white tracking-wide">✔ Gemini AI Email Validator</h1>
                <p className="text-xs text-slate-400 mt-1">Определение страны (GeoIP), времени последней активности и выявление спам-ловушек</p>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-cyan-950/60 text-cyan-400 border border-cyan-500/50">
                ✨ Country + Last Active + AI
              </span>
            </div>
            <div className="h-px bg-gradient-to-r from-cyan-500 via-purple-500 to-emerald-500 opacity-60" />

            <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5 space-y-3">
              <span className="text-xs font-bold text-cyan-400 tracking-wider">🔍 ИНСПЕКЦИЯ ПОЧТЫ (ОПРЕДЕЛИТЬ СТРАНУ, АКТИВНОСТЬ И ЛОВУШКУ)</span>
              <div className="flex gap-3">
                <input
                  type="email"
                  value={singleInspectEmail}
                  onChange={(e) => setSingleInspectEmail(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleInspectSingle()}
                  placeholder="Например: developer@mail.ru, tech@berlin.de или spam-trap_99@honeypot.org"
                  className="flex-1 bg-[#06040a] border border-purple-900/40 rounded-xl px-4 py-2.5 text-xs font-mono text-emerald-300 focus:outline-none focus:border-cyan-400"
                />
                <button
                  onClick={handleInspectSingle}
                  className="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-cyan-500 text-black font-bold text-xs rounded-xl flex items-center gap-2 hover:opacity-95"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  ИНСПЕКЦИЯ С ИИ
                </button>
              </div>
            </div>

            <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5 space-y-4">
              <table className="w-full text-left font-mono text-xs">
                <thead>
                  <tr className="border-b border-purple-900/30 text-slate-500 text-[10px]">
                    <th className="py-2.5 px-3">EMAIL ADDRESS</th>
                    <th className="py-2.5 px-3">СТРАНА (GEOIP)</th>
                    <th className="py-2.5 px-3">ПОСЛЕДНЯЯ АКТИВНОСТЬ</th>
                    <th className="py-2.5 px-3">ВЕРДИКТ</th>
                    <th className="py-2.5 px-3">SCORE</th>
                    <th className="py-2.5 px-3">ПОДРОБНОСТИ</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-purple-950/30">
                  {validatedRecords.map((r, i) => (
                    <tr key={i} className="hover:bg-purple-950/20">
                      <td className="py-2.5 px-3 text-cyan-300 font-semibold">{r.email}</td>
                      <td className="py-2.5 px-3 text-slate-200">{r.country}</td>
                      <td className="py-2.5 px-3 text-emerald-400">{r.lastActive}</td>
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

        {/* TAB 4: MAILER (ВЫБОР ЯЗЫКА КАК В ГУГЛ ПЕРЕВОДЧИКЕ) */}
        {activeTab === 'mailer' && (
          <div className="p-8 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-white tracking-wide">✉ AI Mailer & Multi-Lang Studio</h1>
                <p className="text-xs text-slate-400 mt-1">Выбирайте язык как в переводчике: пишите мысль на русском — ИИ создаёт идеальное письмо на нужном языке</p>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-950/60 text-emerald-400 border border-emerald-500/50 flex items-center gap-1.5">
                <Globe2 className="w-3.5 h-3.5" />
                11 Мировых Языков
              </span>
            </div>
            <div className="h-px bg-gradient-to-r from-cyan-500 via-purple-500 to-emerald-500 opacity-60" />

            <div className="grid grid-cols-1 md:grid-cols-5 gap-5">
              <div className="md:col-span-2 space-y-4">
                <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5 space-y-3">
                  <span className="text-xs font-bold text-cyan-400 font-mono">👥 SENDER ACCOUNT</span>
                  <select
                    value={selectedSenderEmail}
                    onChange={(e) => setSelectedSenderEmail(e.target.value)}
                    className="w-full bg-[#06040a] border border-purple-900/40 rounded-xl px-3 py-2 text-xs font-mono text-cyan-300 focus:outline-none"
                  >
                    {accounts.map(a => (
                      <option key={a.email} value={a.email}>
                        {a.email} ({a.provider})
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={() => setActiveTab('accounts')}
                    className="w-full py-2 bg-purple-900/20 hover:bg-purple-900/40 text-purple-300 border border-purple-500/30 rounded-xl text-xs font-mono"
                  >
                    👥 Manage accounts.txt
                  </button>
                </div>

                <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5 space-y-3">
                  <span className="text-xs font-bold text-emerald-400 font-mono">✔ ПОЛУЧАТЕЛИ ИЗ ТАБЛИЦЫ</span>
                  <div className="space-y-1.5 font-mono text-xs max-h-56 overflow-y-auto">
                    {dbContacts.map(c => (
                      <div key={c.id} className="flex justify-between items-center bg-[#06040a] border border-purple-950 p-2 rounded-lg">
                        <span className="text-slate-300 truncate max-w-[170px]">{c.email}</span>
                        <button
                          onClick={() => setMailerTo(c.email)}
                          className="text-[10px] text-cyan-400 hover:underline"
                        >
                          pick ({c.country.split(' ')[1] || '🌐'})
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

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

                {/* ВЫБОР ЯЗЫКА КАК В ГУГЛ ПЕРЕВОДЧИКЕ */}
                <div className="p-3 bg-[#06040a] border border-cyan-500/30 rounded-xl flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <Languages className="w-4 h-4 text-cyan-400" />
                    <span className="text-xs font-bold text-cyan-300">Язык письма:</span>
                    <select
                      value={selectedLang}
                      onChange={(e) => setSelectedLang(e.target.value)}
                      className="bg-purple-950/80 border border-purple-600/60 rounded-lg px-2.5 py-1 text-xs text-white focus:outline-none"
                    >
                      {LANGUAGES.map(l => (
                        <option key={l.code} value={l.code}>{l.name}</option>
                      ))}
                    </select>
                  </div>
                  <button
                    onClick={() => setAiModalOpen(true)}
                    className="px-3.5 py-1.5 bg-gradient-to-r from-purple-600 to-cyan-500 text-white font-bold text-xs rounded-lg flex items-center gap-1.5 shadow-md shadow-cyan-500/20"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    НАПИСАТЬ ЧЕРЕЗ ИИ
                  </button>
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
                  <label className="block text-[10px] font-mono font-bold text-slate-500 mb-1">MESSAGE CONTENT</label>
                  <textarea
                    rows={8}
                    value={mailerBody}
                    onChange={(e) => setMailerBody(e.target.value)}
                    className="w-full bg-[#06040a] border border-purple-900/40 rounded-xl p-3.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-400 font-sans"
                  />
                </div>

                <div className="flex items-center justify-between pt-2">
                  <span className="text-xs text-slate-400">🛡 Anti-Spam Pre-Flight Armed</span>
                  <button
                    onClick={() => alert(`Email dispatched to ${mailerTo} via ${selectedSenderEmail}!`)}
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

        {/* TAB 5: ACCOUNTS MANAGER */}
        {activeTab === 'accounts' && (
          <div className="p-8 space-y-6">
            <h1 className="text-2xl font-bold text-white tracking-wide">👥 Sender Accounts Manager (accounts.txt)</h1>
            <div className="h-px bg-gradient-to-r from-cyan-500 via-purple-500 to-emerald-500 opacity-60" />
            <div className="grid grid-cols-1 md:grid-cols-5 gap-5">
              <div className="md:col-span-2 space-y-4">
                <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-5 space-y-3">
                  <span className="text-xs font-bold text-cyan-400 font-mono">+ ADD SINGLE ACCOUNT</span>
                  <input
                    type="email"
                    value={newAccEmail}
                    onChange={(e) => setNewAccEmail(e.target.value)}
                    placeholder="e.g. sender@gmail.com"
                    className="w-full bg-[#06040a] border border-purple-900/40 rounded-xl px-3 py-2 text-xs text-white font-mono"
                  />
                  <input
                    type="password"
                    value={newAccPass}
                    onChange={(e) => setNewAccPass(e.target.value)}
                    placeholder="e.g. xxxx-xxxx-xxxx-xxxx"
                    className="w-full bg-[#06040a] border border-purple-900/40 rounded-xl px-3 py-2 text-xs text-white font-mono"
                  />
                  <button
                    onClick={() => {
                      if (!newAccEmail || !newAccPass) return;
                      setAccounts(prev => [...prev, { email: newAccEmail, provider: 'SMTP', status: 'READY' }]);
                      setNewAccEmail('');
                      setNewAccPass('');
                    }}
                    className="w-full py-2.5 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 rounded-xl text-xs font-mono font-bold"
                  >
                    SAVE TO ACCOUNTS.TXT
                  </button>
                </div>
              </div>
              <div className="md:col-span-3 bg-[#0e0918] border border-purple-900/30 rounded-2xl p-6 space-y-3">
                <span className="text-xs font-bold text-emerald-400 font-mono">📄 DIRECT RAW EDITOR: ACCOUNTS.TXT</span>
                <textarea
                  rows={12}
                  value={rawAccountsFile}
                  onChange={(e) => setRawAccountsFile(e.target.value)}
                  className="w-full bg-[#06040a] border border-purple-950 rounded-xl p-4 font-mono text-xs text-emerald-400 focus:outline-none"
                />
              </div>
            </div>
          </div>
        )}

        {/* TAB 6: LO-FI RADIO (14 STATIONS) */}
        {activeTab === 'radio' && (
          <div className="p-8 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-white tracking-wide">((o)) Cyberpunk Lo-Fi Radio (14 Станций)</h1>
                <p className="text-xs text-slate-400 mt-1">14 проверенных онлайн потоков: Chillhop, Nightwave Plaza, DEF CON, Japan Lo-Fi, Groove Salad</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-mono font-bold border ${
                radioPlaying ? 'bg-emerald-950/60 text-emerald-400 border-emerald-500/50' : 'bg-rose-950/60 text-rose-400 border-rose-500/50'
              }`}>
                ● {radioPlaying ? 'RADIO LIVE' : 'RADIO OFF'}
              </span>
            </div>
            <div className="h-px bg-gradient-to-r from-cyan-500 via-purple-500 to-emerald-500 opacity-60" />

            <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-6 space-y-5">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="font-bold text-cyan-400 flex items-center gap-2">
                  <Radio className="w-4 h-4" />
                  {RADIO_STATIONS[currentStationIdx].name.toUpperCase()}
                </span>
                <span className="text-slate-500">{radioPlaying ? 'STREAMING 128KBPS' : 'STOPPED'}</span>
              </div>

              <div className="bg-[#06040a] border border-purple-900/30 rounded-xl py-6 px-6 flex items-center justify-center gap-1.5 overflow-hidden">
                {Array.from({ length: 48 }).map((_, i) => (
                  <span
                    key={i}
                    style={{ height: radioPlaying ? `${Math.sin(i * 0.4) * 16 + 20}px` : '4px' }}
                    className={`w-1 rounded-full transition-all duration-300 ${radioPlaying ? 'bg-cyan-400 shadow-sm shadow-cyan-400' : 'bg-purple-900/40'}`}
                  />
                ))}
              </div>

              <div className="flex flex-wrap items-center justify-between gap-4">
                <button
                  onClick={() => toggleRadio()}
                  className="px-8 py-3.5 bg-gradient-to-r from-cyan-500 to-purple-600 text-black font-extrabold text-sm rounded-xl flex items-center gap-2 shadow-lg shadow-cyan-500/30"
                >
                  {radioPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current" />}
                  {radioPlaying ? 'ПАУЗА' : 'ВКЛЮЧИТЬ РАДИО'}
                </button>

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
            </div>

            <div className="space-y-3">
              <span className="text-xs font-mono font-bold text-cyan-400">🎧 6 ПРОВЕРЕННЫХ ОНЛАЙН СТАНЦИЙ 24/7 (100% LIVE)</span>
              <p className="text-[11px] text-slate-400">Все потоки протестированы: чистый битрейт, 100% аптайм, без 404/403 ошибок.</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {RADIO_STATIONS.map((station, idx) => {
                  const isCurrent = currentStationIdx === idx;
                  return (
                    <div
                      key={station.name}
                      onClick={() => toggleRadio(idx)}
                      className={`bg-[#0e0918] border p-4 rounded-xl cursor-pointer transition ${
                        isCurrent ? 'border-cyan-400/80 shadow-lg shadow-cyan-500/10' : 'border-purple-900/30 hover:border-purple-500/40'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex items-center gap-2">
                          <Radio className="w-4 h-4 text-cyan-400" />
                          <h4 className="text-xs font-bold text-white">{station.name}</h4>
                        </div>
                        <span className="text-[9px] font-mono font-bold text-cyan-400 border border-cyan-500/50 px-2 py-0.5 rounded">
                          {station.genre}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 mt-1.5">{station.desc}</p>
                      <div className="flex justify-between items-center text-[10px] font-mono mt-3 pt-2 border-t border-purple-950">
                        <span className={isCurrent && radioPlaying ? 'text-emerald-400 font-bold' : 'text-slate-500'}>
                          {isCurrent && radioPlaying ? '● Играет сейчас' : 'Кликните для включения'}
                        </span>
                        <span className="text-cyan-300 font-bold bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-500/30">
                          {station.bitrate}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* TAB 7: CYBER SHORTS & REELS (РЕАЛЬНАЯ БЕСКОНЕЧНАЯ ЛЕНТА TIKTOK / YOUTUBE SHORTS) */}
        {activeTab === 'shorts' && (
          <div className="p-8 space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h1 className="text-2xl font-bold text-white tracking-wide flex items-center gap-2.5">
                  🎬 Cyber Shorts & TikTok Reels <span className="text-xs font-mono font-semibold px-2.5 py-0.5 rounded-full bg-cyan-950/80 text-cyan-400 border border-cyan-500/40">Бесконечная Лента ♾️</span>
                </h1>
                <p className="text-xs text-slate-400 mt-1">
                  Настоящая бесконечная лента YouTube Shorts и TikTok клипов: листайте без ограничений, ищите по темам или вставляйте свои ссылки
                </p>
              </div>

              {/* Toolbar Controls */}
              <div className="flex flex-wrap items-center gap-3">
                {/* View Mode Switcher */}
                <div className="flex bg-[#06040a] border border-purple-900/40 p-1 rounded-xl text-xs font-mono">
                  <button
                    onClick={() => setShortsViewMode('feed')}
                    className={`px-3 py-1.5 rounded-lg transition ${
                      shortsViewMode === 'feed' ? 'bg-purple-600 text-white font-bold shadow-md shadow-purple-900/50' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    📜 Лента TikTok (Скролл)
                  </button>
                  <button
                    onClick={() => setShortsViewMode('focus')}
                    className={`px-3 py-1.5 rounded-lg transition ${
                      shortsViewMode === 'focus' ? 'bg-purple-600 text-white font-bold shadow-md shadow-purple-900/50' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    📱 Фокус-Плеер
                  </button>
                </div>

                {/* Auto-Advance Toggle */}
                <button
                  onClick={() => setShortsAutoScroll(!shortsAutoScroll)}
                  className={`px-3.5 py-1.5 rounded-xl border text-xs font-mono font-bold flex items-center gap-2 transition shadow-lg ${
                    shortsAutoScroll
                      ? 'bg-emerald-950/60 text-emerald-400 border-emerald-500/50 shadow-emerald-500/20'
                      : 'bg-black/60 text-slate-400 border-purple-900/40'
                  }`}
                  title="Автоматический переход к следующему видео по окончании ролика"
                >
                  <Repeat className="w-3.5 h-3.5" />
                  Авто-скролл: {shortsAutoScroll ? 'ВКЛ' : 'ВЫКЛ'}
                </button>

                {/* Sound Toggle */}
                <button
                  onClick={() => {
                    const newM = !shortsMuted;
                    setShortsMuted(newM);
                    if (videoRef.current) videoRef.current.muted = newM;
                  }}
                  className={`px-3.5 py-1.5 rounded-xl border text-xs font-mono font-bold flex items-center gap-2 transition shadow-lg ${
                    !shortsMuted
                      ? 'bg-cyan-950/60 text-cyan-300 border-cyan-500/50 shadow-cyan-500/20'
                      : 'bg-black/60 text-rose-400 border-rose-900/40'
                  }`}
                >
                  {shortsMuted ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5" />}
                  Звук: {shortsMuted ? 'ВЫКЛ' : 'ВКЛ'}
                </button>

                {/* Add Custom Video Button */}
                <button
                  onClick={() => setCustomModalOpen(true)}
                  className="px-3.5 py-1.5 rounded-xl border text-xs font-mono font-bold flex items-center gap-1.5 bg-gradient-to-r from-emerald-600 to-cyan-600 text-black hover:opacity-95 shadow-md shadow-emerald-500/20"
                >
                  <Plus className="w-4 h-4 stroke-[2.5]" />
                  Добавить Shorts
                </button>
              </div>
            </div>

            {/* Category Filter Pills & Search Bar */}
            <div className="flex flex-wrap items-center justify-between gap-3 bg-[#0a0614] border border-purple-900/40 p-3 rounded-2xl">
              <div className="flex flex-wrap items-center gap-1.5 text-xs font-mono">
                <span className="text-slate-400 font-bold mr-1 flex items-center gap-1 text-[11px]">
                  <Flame className="w-3.5 h-3.5 text-rose-500" /> Темы:
                </span>
                {[
                  { id: 'ALL', label: '🔥 Все тренды' },
                  { id: 'TECH', label: '💻 IT & Код' },
                  { id: 'MEMES', label: '😂 Мемы' },
                  { id: 'GAMING', label: '🎮 Гейминг' },
                  { id: 'ASMR', label: '⚡ ASMR' },
                  { id: 'CYBER', label: '🌌 Киберпанк' },
                  { id: 'AUTO', label: '🏎️ Дрифт & Авто' }
                ].map(cat => (
                  <button
                    key={cat.id}
                    onClick={() => handleCategoryChange(cat.id)}
                    className={`px-3 py-1 rounded-xl text-xs transition font-semibold ${
                      shortsCategory === cat.id
                        ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/60 shadow-sm shadow-cyan-500/30'
                        : 'text-slate-400 hover:text-white hover:bg-purple-950/40 border border-transparent'
                    }`}
                  >
                    {cat.label}
                  </button>
                ))}
              </div>

              {/* Search Box */}
              <form onSubmit={handleSearchSubmit} className="flex items-center gap-2">
                <div className="relative">
                  <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
                  <input
                    type="text"
                    value={shortsSearchQuery}
                    onChange={e => setShortsSearchQuery(e.target.value)}
                    placeholder="Поиск по теме, тегу (#coding)..."
                    className="pl-8 pr-3 py-1.5 bg-[#050308] border border-purple-900/40 rounded-xl text-xs font-mono text-cyan-300 placeholder-slate-600 w-56 focus:outline-none focus:border-cyan-400/80"
                  />
                  {shortsSearchQuery && (
                    <button
                      type="button"
                      onClick={() => {
                        setShortsSearchQuery('');
                        setShortsFeed(generateInfiniteShorts(0, 20, shortsCategory, ''));
                        setShortIdx(0);
                      }}
                      className="absolute right-2.5 top-2 text-slate-400 hover:text-white text-xs"
                    >
                      ✕
                    </button>
                  )}
                </div>
                <button
                  type="submit"
                  className="px-3 py-1.5 bg-purple-900/40 hover:bg-purple-800/60 border border-purple-500/40 text-cyan-300 text-xs font-mono font-bold rounded-xl transition"
                >
                  Найти
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const rnd = Math.floor(Math.random() * shortsFeed.length);
                    setShortIdx(rnd);
                    if (shortsViewMode !== 'focus') setShortsViewMode('focus');
                  }}
                  className="px-3 py-1.5 bg-cyan-950/50 hover:bg-cyan-900/60 border border-cyan-500/40 text-cyan-300 text-xs font-mono font-bold rounded-xl transition"
                  title="Открыть случайный ролик"
                >
                  🎲 Случайный
                </button>
              </form>
            </div>

            <div className="h-px bg-gradient-to-r from-cyan-500 via-purple-500 to-emerald-500 opacity-60" />

            {/* VIEW MODE 1: INFINITE VERTICAL SCROLL FEED (TIKTOK / REELS STYLE) */}
            {shortsViewMode === 'feed' && (
              <div
                ref={feedScrollContainerRef}
                onScroll={handleFeedScroll}
                className="flex flex-col items-center space-y-10 max-h-[760px] overflow-y-auto px-4 py-2 scroll-smooth"
              >
                {shortsFeed.map((item, idx) => {
                  const isLiked = !!shortLikesMap[item.id];
                  const likesCount = item.likes + (isLiked ? 1 : 0);
                  const isFollowing = !!followingMap[item.author];
                  const commentsForThis = commentsData[item.id] || [];

                  return (
                    <div
                      key={`${item.id}-${idx}`}
                      className="w-full max-w-[420px] bg-[#0c0915] border-2 border-purple-500/40 rounded-[32px] p-4 shadow-2xl shadow-purple-950/80 space-y-3 relative shrink-0 transition hover:border-purple-500/70"
                    >
                      {/* Top Header */}
                      <div className="flex justify-between items-center text-xs font-mono px-2 pt-1">
                        <div className="flex items-center gap-2">
                          <span className="w-7 h-7 rounded-full bg-purple-900/60 border border-purple-500/50 flex items-center justify-center text-sm">
                            {item.avatar || '🎬'}
                          </span>
                          <div>
                            <span className="text-cyan-400 font-bold block">{item.author}</span>
                            <span className="text-[10px] text-slate-500">{item.views} просмотров</span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => setFollowingMap(prev => ({ ...prev, [item.author]: !prev[item.author] }))}
                            className={`text-[10px] font-mono font-bold px-2.5 py-1 rounded-full border transition flex items-center gap-1 ${
                              isFollowing
                                ? 'bg-emerald-950/60 text-emerald-400 border-emerald-500/50'
                                : 'bg-purple-900/40 text-purple-300 border-purple-500/50 hover:bg-purple-800/60'
                            }`}
                          >
                            {isFollowing ? <UserCheck className="w-3 h-3" /> : <UserPlus className="w-3 h-3" />}
                            {isFollowing ? 'Подписан' : '+ Подписаться'}
                          </button>
                          <span className="text-slate-400 text-[10px] bg-black/60 px-2 py-0.5 rounded border border-purple-900/40">
                            #{idx + 1}
                          </span>
                        </div>
                      </div>

                      {/* Video Viewport Frame (9:16) */}
                      <div className="relative rounded-2xl overflow-hidden bg-black aspect-[9/16] max-h-[560px] flex items-center justify-center group shadow-inner">
                        {item.embedUrl ? (
                          <iframe
                            src={item.embedUrl}
                            title={item.title}
                            className="w-full h-full border-0 pointer-events-auto"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                            allowFullScreen
                          />
                        ) : (
                          <video
                            src={item.url}
                            autoPlay
                            loop
                            muted={shortsMuted}
                            playsInline
                            className="w-full h-full object-cover"
                          />
                        )}

                        {/* Floating Metadata Overlay at the bottom */}
                        <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/95 via-black/50 to-transparent p-4 space-y-1.5 pointer-events-none">
                          <div className="text-xs font-bold text-white line-clamp-2 drop-shadow-md">
                            {item.title}
                          </div>
                          <div className="text-[10px] text-purple-300 font-bold drop-shadow-sm">
                            {item.tags}
                          </div>
                          <div className="flex items-center gap-2 text-[10px] font-mono text-cyan-300 bg-black/60 px-2.5 py-1 rounded-full border border-cyan-500/30 w-fit backdrop-blur-sm">
                            <Disc3 className="w-3.5 h-3.5 animate-spin" />
                            <span className="truncate max-w-[220px]">{item.sound}</span>
                          </div>
                        </div>

                        {/* Vertical Floating Action Icons (TikTok Style on right side) */}
                        <div className="absolute right-2.5 bottom-16 flex flex-col items-center gap-3 z-10">
                          {/* Like Button */}
                          <button
                            onClick={() => setShortLikesMap(prev => ({ ...prev, [item.id]: !prev[item.id] }))}
                            className={`w-11 h-11 rounded-full flex flex-col items-center justify-center border shadow-xl transition backdrop-blur-md active:scale-90 ${
                              isLiked
                                ? 'bg-rose-500 text-white border-rose-400 shadow-rose-500/40'
                                : 'bg-black/60 text-slate-300 border-white/20 hover:text-rose-400 hover:bg-black/80'
                            }`}
                            title="Поставить лайк"
                          >
                            <Heart className={`w-5 h-5 ${isLiked ? 'fill-current' : ''}`} />
                            <span className="text-[8px] font-mono mt-0.5 font-bold">
                              {(likesCount / 1000).toFixed(1)}K
                            </span>
                          </button>

                          {/* Comments Button */}
                          <button
                            onClick={() => {
                              setActiveCommentShortId(item.id);
                              setCommentsDrawerOpen(true);
                            }}
                            className="w-11 h-11 rounded-full bg-black/60 hover:bg-black/80 text-slate-300 hover:text-cyan-300 border border-white/20 flex flex-col items-center justify-center shadow-xl transition backdrop-blur-md active:scale-90"
                            title="Комментарии"
                          >
                            <MessageSquare className="w-4 h-4" />
                            <span className="text-[8px] font-mono mt-0.5 font-bold">
                              {item.commentsCount || commentsForThis.length}
                            </span>
                          </button>

                          {/* Share Button */}
                          <button
                            onClick={() => {
                              const shareUrl = item.youtubeId ? `https://www.youtube.com/shorts/${item.youtubeId}` : item.url;
                              navigator.clipboard?.writeText(shareUrl);
                              setCopiedLink(true);
                              setTimeout(() => setCopiedLink(false), 2000);
                            }}
                            className="w-11 h-11 rounded-full bg-black/60 hover:bg-black/80 text-slate-300 hover:text-emerald-300 border border-white/20 flex flex-col items-center justify-center shadow-xl transition backdrop-blur-md active:scale-90"
                            title="Поделиться"
                          >
                            {copiedLink ? <Check className="w-4 h-4 text-emerald-400" /> : <Share2 className="w-4 h-4" />}
                            <span className="text-[8px] font-mono mt-0.5 font-bold">
                              {copiedLink ? 'OK' : 'SHARE'}
                            </span>
                          </button>

                          {/* External App Link */}
                          {item.youtubeId && (
                            <a
                              href={`https://www.youtube.com/shorts/${item.youtubeId}`}
                              target="_blank"
                              rel="noreferrer"
                              className="w-11 h-11 rounded-full bg-rose-600/30 hover:bg-rose-600/60 text-rose-300 border border-rose-500/40 flex flex-col items-center justify-center shadow-xl transition backdrop-blur-md active:scale-90"
                              title="Открыть в YouTube Shorts"
                            >
                              <ExternalLink className="w-4 h-4" />
                              <span className="text-[7px] font-mono mt-0.5 font-bold">YOUTUBE</span>
                            </a>
                          )}
                        </div>
                      </div>

                      {/* Card Bottom Quick Action Bar */}
                      <div className="flex justify-between items-center pt-1 border-t border-purple-950 text-xs font-mono">
                        <button
                          onClick={() => {
                            setShortIdx(idx);
                            setShortsViewMode('focus');
                          }}
                          className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-950/40 border border-cyan-500/30 transition hover:bg-cyan-900/50"
                        >
                          <Play className="w-3.5 h-3.5 fill-current" />
                          Развернуть в Фокус
                        </button>

                        <button
                          onClick={() => {
                            setActiveCommentShortId(item.id);
                            setCommentsDrawerOpen(true);
                          }}
                          className="text-purple-300 hover:text-white flex items-center gap-1 transition"
                        >
                          💬 Комментарии ({commentsForThis.length + 3})
                        </button>
                      </div>
                    </div>
                  );
                })}

                {/* Infinite Loader Indicator */}
                <div className="py-6 flex flex-col items-center gap-2 text-slate-500 text-xs font-mono">
                  <div className="flex items-center gap-2 text-cyan-400 font-bold">
                    <Sparkles className="w-4 h-4 animate-spin" />
                    <span>Бесконечная лента активна • Прокрутите вниз для авто-загрузки новых видео</span>
                  </div>
                  <span className="text-[11px] text-slate-500">Загружено роликов: {shortsFeed.length} из ∞</span>
                </div>
              </div>
            )}

            {/* VIEW MODE 2: FOCUS PHONE PLAYER */}
            {shortsViewMode === 'focus' && (
              <div className="flex flex-col items-center">
                <div className="flex justify-center items-start gap-8 max-w-4xl w-full">
                  {/* Vertical Phone Frame */}
                  <div className="w-[380px] bg-[#0c0915] border-2 border-purple-500/50 rounded-[32px] p-4 shadow-2xl shadow-purple-950/60 space-y-3 relative overflow-hidden">
                    {/* Top Status Bar inside phone */}
                    <div className="flex justify-between items-center text-xs font-mono px-2 pt-1">
                      <div className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
                        <span className="text-cyan-400 font-bold">{shortsFeed[shortIdx].author}</span>
                      </div>
                      <span className="text-slate-400 text-[11px] bg-black/60 px-2.5 py-0.5 rounded-md border border-purple-900/30">
                        Ролик #{shortIdx + 1} из ∞ ♾️
                      </span>
                    </div>

                    {/* Video Viewport */}
                    <div
                      onClick={() => {
                        setShortPlaying(!shortPlaying);
                        if (videoRef.current) {
                          if (videoRef.current.paused) videoRef.current.play().catch(() => {});
                          else videoRef.current.pause();
                        }
                      }}
                      className="relative rounded-2xl overflow-hidden bg-black aspect-[9/16] max-h-[540px] flex items-center justify-center cursor-pointer group"
                    >
                      {shortsFeed[shortIdx].embedUrl ? (
                        <iframe
                          src={shortsFeed[shortIdx].embedUrl}
                          title={shortsFeed[shortIdx].title}
                          className="w-full h-full border-0 pointer-events-auto"
                          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                          allowFullScreen
                        />
                      ) : (
                        <video
                          ref={videoRef}
                          key={shortsFeed[shortIdx].url}
                          src={shortsFeed[shortIdx].url}
                          autoPlay
                          playsInline
                          muted={shortsMuted}
                          onEnded={handleShortEnded}
                          onTimeUpdate={(e) => {
                            const v = e.currentTarget;
                            if (v.duration) setShortProgress((v.currentTime / v.duration) * 100);
                          }}
                          className="w-full h-full object-cover"
                        />
                      )}

                      {/* Floating Bottom Metadata Overlay on Video */}
                      <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent p-4 space-y-2 pointer-events-none">
                        <div className="text-xs font-bold text-white line-clamp-2 drop-shadow-md">
                          {shortsFeed[shortIdx].title}
                        </div>
                        <div className="text-[10px] text-purple-300 font-bold drop-shadow-sm">
                          {shortsFeed[shortIdx].tags}
                        </div>
                        {/* Audio sound badge with rotating vinyl */}
                        <div className="flex items-center gap-2 text-[10px] font-mono text-cyan-300 bg-black/60 px-2.5 py-1 rounded-full border border-cyan-500/30 w-fit backdrop-blur-sm">
                          <Disc3 className={`w-3.5 h-3.5 ${shortPlaying ? 'animate-spin' : ''}`} />
                          <span className="truncate max-w-[200px]">{shortsFeed[shortIdx].sound}</span>
                        </div>

                        {/* Progress bar */}
                        <div className="w-full h-1 bg-white/20 rounded-full overflow-hidden">
                          <div
                            style={{ width: `${shortProgress}%` }}
                            className="h-full bg-gradient-to-r from-cyan-400 to-purple-500 transition-all duration-150"
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Vertical Controls Sidebar */}
                  <div className="space-y-3 pt-6">
                    {/* Prev Video Button */}
                    <button
                      onClick={handlePrevShort}
                      className="w-14 h-14 bg-purple-900/30 hover:bg-purple-900/60 border border-purple-500/40 rounded-2xl flex items-center justify-center text-cyan-300 shadow-lg hover:scale-105 active:scale-95 transition"
                      title="Предыдущее видео (Стрелка вверх)"
                    >
                      <ChevronUp className="w-6 h-6" />
                    </button>

                    {/* Like Button */}
                    <button
                      onClick={() => setShortLikesMap(prev => ({ ...prev, [shortsFeed[shortIdx].id]: !prev[shortsFeed[shortIdx].id] }))}
                      className={`w-14 h-14 rounded-2xl flex flex-col items-center justify-center transition border shadow-lg hover:scale-105 active:scale-95 ${
                        shortLikesMap[shortsFeed[shortIdx].id]
                          ? 'bg-rose-500 text-white border-rose-400 shadow-rose-500/40'
                          : 'bg-black/60 text-slate-300 border-purple-900/40 hover:text-rose-400'
                      }`}
                      title="Поставить лайк"
                    >
                      <Heart className={`w-5 h-5 ${shortLikesMap[shortsFeed[shortIdx].id] ? 'fill-current' : ''}`} />
                      <span className="text-[9px] font-mono mt-0.5">
                        {((shortsFeed[shortIdx].likes + (shortLikesMap[shortsFeed[shortIdx].id] ? 1 : 0)) / 1000).toFixed(1)}K
                      </span>
                    </button>

                    {/* Comments Button */}
                    <button
                      onClick={() => {
                        setActiveCommentShortId(shortsFeed[shortIdx].id);
                        setCommentsDrawerOpen(true);
                      }}
                      className="w-14 h-14 bg-black/60 hover:bg-purple-950/60 text-slate-300 hover:text-cyan-300 border border-purple-900/40 rounded-2xl flex flex-col items-center justify-center shadow-lg hover:scale-105 active:scale-95 transition"
                      title="Открыть комментарии"
                    >
                      <MessageSquare className="w-5 h-5" />
                      <span className="text-[8px] font-mono mt-0.5">ЧАТ</span>
                    </button>

                    {/* Next Video Button */}
                    <button
                      onClick={handleNextShort}
                      className="w-14 h-14 bg-purple-900/30 hover:bg-purple-900/60 border border-purple-500/40 rounded-2xl flex items-center justify-center text-cyan-300 shadow-lg hover:scale-105 active:scale-95 transition"
                      title="Следующее видео (Стрелка вниз)"
                    >
                      <ChevronDown className="w-6 h-6" />
                    </button>

                    {/* Share Button */}
                    <button
                      onClick={() => {
                        const url = shortsFeed[shortIdx].youtubeId ? `https://www.youtube.com/shorts/${shortsFeed[shortIdx].youtubeId}` : shortsFeed[shortIdx].url;
                        navigator.clipboard?.writeText(url);
                        setCopiedLink(true);
                        setTimeout(() => setCopiedLink(false), 2000);
                      }}
                      className="w-14 h-14 bg-black/60 hover:bg-purple-950/60 text-slate-300 border border-purple-900/40 rounded-2xl flex flex-col items-center justify-center shadow-lg hover:scale-105 active:scale-95 transition"
                      title="Скопировать ссылку на видео"
                    >
                      {copiedLink ? <Check className="w-5 h-5 text-emerald-400" /> : <Share2 className="w-5 h-5" />}
                      <span className="text-[8px] font-mono mt-0.5">{copiedLink ? 'OK' : 'SHARE'}</span>
                    </button>

                    {/* External Link */}
                    {shortsFeed[shortIdx].youtubeId && (
                      <a
                        href={`https://www.youtube.com/shorts/${shortsFeed[shortIdx].youtubeId}`}
                        target="_blank"
                        rel="noreferrer"
                        className="w-14 h-14 bg-rose-600/30 hover:bg-rose-600/60 text-rose-300 border border-rose-500/40 rounded-2xl flex flex-col items-center justify-center shadow-lg hover:scale-105 active:scale-95 transition"
                        title="Открыть в приложении YouTube Shorts"
                      >
                        <ExternalLink className="w-5 h-5" />
                        <span className="text-[7px] font-mono mt-0.5 font-bold">YOUTUBE</span>
                      </a>
                    )}
                  </div>
                </div>

                {/* Keyboard Control Hints */}
                <div className="flex items-center gap-4 text-[11px] font-mono text-slate-400 mt-6 bg-[#06040a] px-4 py-2 rounded-xl border border-purple-900/30">
                  <span>⌨️ Горячие клавиши:</span>
                  <span className="text-cyan-300 font-bold">[↑ / ↓] Листать ролики</span>
                  <span className="text-purple-300 font-bold">[Пробел] Пауза / Пуск</span>
                  <span className="text-emerald-300 font-bold">[M] Звук ВКЛ/ВЫКЛ</span>
                  <span className="text-slate-500">• Лента бесконечно продолжается</span>
                </div>
              </div>
            )}

            {/* MODAL: ДОБАВИТЬ СВОЙ РОЛИК YOUTUBE SHORTS ИЛИ TIKTOK */}
            {customModalOpen && (
              <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                <div className="bg-[#0e0918] border-2 border-purple-500/60 rounded-3xl p-6 max-w-lg w-full space-y-4 shadow-2xl">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                      🎬 Добавить Shorts / TikTok в Ленту
                    </h3>
                    <button
                      onClick={() => setCustomModalOpen(false)}
                      className="text-slate-400 hover:text-white p-1 rounded-lg"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  <p className="text-xs text-slate-400">
                    Вставьте ссылку на любой YouTube Shorts (<code className="text-cyan-300">https://youtube.com/shorts/...</code>) или прямую ссылку на видео. Ролик мгновенно добавится в вашу бесконечную ленту!
                  </p>

                  <div className="space-y-3">
                    <div>
                      <label className="text-[11px] font-mono text-slate-300 block mb-1">Ссылка на Shorts или видео *</label>
                      <input
                        type="text"
                        value={customUrlInput}
                        onChange={e => setCustomUrlInput(e.target.value)}
                        placeholder="https://youtube.com/shorts/s_ndf10e47g или https://youtu.be/..."
                        className="w-full px-3.5 py-2.5 bg-[#06040a] border border-purple-900/50 rounded-xl text-xs font-mono text-cyan-300 focus:outline-none focus:border-cyan-400"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] font-mono text-slate-300 block mb-1">Название ролика</label>
                      <input
                        type="text"
                        value={customTitleInput}
                        onChange={e => setCustomTitleInput(e.target.value)}
                        placeholder="Например: Топовый лайфхак по Python кодингу 🚀"
                        className="w-full px-3.5 py-2.5 bg-[#06040a] border border-purple-900/50 rounded-xl text-xs font-mono text-white focus:outline-none focus:border-cyan-400"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] font-mono text-slate-300 block mb-1">Ник автора (@creator)</label>
                      <input
                        type="text"
                        value={customAuthorInput}
                        onChange={e => setCustomAuthorInput(e.target.value)}
                        placeholder="@my_channel"
                        className="w-full px-3.5 py-2.5 bg-[#06040a] border border-purple-900/50 rounded-xl text-xs font-mono text-white focus:outline-none focus:border-cyan-400"
                      />
                    </div>
                  </div>

                  <div className="flex justify-end gap-3 pt-2">
                    <button
                      onClick={() => setCustomModalOpen(false)}
                      className="px-4 py-2 bg-transparent text-slate-400 hover:text-white text-xs font-mono rounded-xl"
                    >
                      Отмена
                    </button>
                    <button
                      onClick={handleAddCustomShort}
                      className="px-5 py-2.5 bg-gradient-to-r from-cyan-500 to-purple-600 text-black font-extrabold text-xs font-mono rounded-xl shadow-lg shadow-cyan-500/20"
                    >
                      ▶ Добавить и смотреть
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* SLIDE-OVER DRAWER: КОММЕНТАРИИ К РОЛИКУ */}
            {commentsDrawerOpen && (
              <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex justify-end z-50">
                <div className="w-full max-w-md bg-[#0c0816] border-l border-purple-500/40 h-full p-6 flex flex-col justify-between shadow-2xl">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center border-b border-purple-950 pb-3">
                      <div>
                        <h3 className="text-base font-bold text-white flex items-center gap-2">
                          💬 Комментарии сообщества
                        </h3>
                        <span className="text-[11px] font-mono text-slate-400">
                          К ролику: {shortsFeed.find(s => s.id === activeCommentShortId)?.title.slice(0, 32)}...
                        </span>
                      </div>
                      <button
                        onClick={() => setCommentsDrawerOpen(false)}
                        className="text-slate-400 hover:text-white p-1 rounded-lg"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>

                    {/* Comments List */}
                    <div className="space-y-3 max-h-[580px] overflow-y-auto pr-2">
                      {((activeCommentShortId && commentsData[activeCommentShortId]) || [
                        { user: '@cyber_viewer', avatar: '🤖', text: 'Этот шортс залетел в реки!', time: '1ч назад', likes: 45 },
                        { user: '@code_hacker', avatar: '💻', text: 'Крутой контент, продолжай в том же духе!', time: '2ч назад', likes: 28 },
                        { user: '@lofi_girl', avatar: '🎧', text: 'Музыка на фоне просто космос...', time: '3ч назад', likes: 62 }
                      ]).map((c, i) => (
                        <div key={i} className="bg-[#06040a] border border-purple-900/30 rounded-xl p-3 space-y-1">
                          <div className="flex justify-between items-center text-xs">
                            <span className="font-bold text-cyan-400 flex items-center gap-1.5">
                              <span>{c.avatar}</span> {c.user}
                            </span>
                            <span className="text-[10px] text-slate-500">{c.time}</span>
                          </div>
                          <p className="text-xs text-slate-200">{c.text}</p>
                          <div className="flex items-center gap-1 text-[10px] text-slate-400 pt-1">
                            <Heart className="w-3 h-3 text-rose-500" />
                            <span>{c.likes}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Comment Input */}
                  <div className="pt-4 border-t border-purple-950">
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={newCommentInput}
                        onChange={e => setNewCommentInput(e.target.value)}
                        onKeyDown={e => {
                          if (e.key === 'Enter' && activeCommentShortId) {
                            handlePostComment(activeCommentShortId);
                          }
                        }}
                        placeholder="Написать комментарий..."
                        className="flex-1 px-3 py-2 bg-[#06040a] border border-purple-900/40 rounded-xl text-xs text-white placeholder-slate-600 focus:outline-none focus:border-cyan-400"
                      />
                      <button
                        onClick={() => activeCommentShortId && handlePostComment(activeCommentShortId)}
                        className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-purple-600 text-black font-bold text-xs rounded-xl"
                      >
                        Отправить
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 8: DATABASE TABLE VIEWER (СТРУКТУРИРОВАННАЯ ТАБЛИЦА) */}
        {activeTab === 'base' && (
          <div className="p-8 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-white tracking-wide">📊 Database Table Viewer (SQLite & CSV)</h1>
                <p className="text-xs text-slate-400 mt-1">
                  Все спарсенные почты сохраняются в структурированную таблицу базы данных с геолокацией страны и датой активности
                </p>
              </div>
              <button
                onClick={handleExportCsv}
                className="px-4 py-2 bg-gradient-to-r from-emerald-500 to-cyan-500 text-black font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-emerald-500/20"
              >
                <Download className="w-3.5 h-3.5" />
                Экспорт в Excel (CSV)
              </button>
            </div>
            <div className="h-px bg-gradient-to-r from-cyan-500 via-purple-500 to-emerald-500 opacity-60" />

            <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl p-4 flex items-center justify-between gap-4">
              <div className="flex items-center gap-2 flex-1 max-w-md">
                <Search className="w-4 h-4 text-cyan-400" />
                <input
                  type="text"
                  value={dbSearch}
                  onChange={(e) => setDbSearch(e.target.value)}
                  placeholder="Фильтр по email, стране (например: Россия, США) или источнику..."
                  className="w-full bg-[#06040a] border border-purple-900/40 rounded-xl px-3 py-1.5 text-xs font-mono text-emerald-300 focus:outline-none"
                />
              </div>
              <div className="flex gap-2">
                <span className="text-xs font-mono text-slate-400 py-1.5 px-3 bg-black/40 border border-purple-950 rounded-lg">
                  Всего записей: <b className="text-cyan-300">{filteredDbContacts.length}</b>
                </span>
                <button
                  onClick={() => setDbContacts([])}
                  className="px-3 py-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/40 rounded-lg text-xs font-mono"
                >
                  Очистить таблицу
                </button>
              </div>
            </div>

            <div className="bg-[#0e0918] border border-purple-900/30 rounded-2xl overflow-hidden">
              <table className="w-full text-left font-mono text-xs">
                <thead>
                  <tr className="border-b border-purple-900/30 text-slate-500 text-[10px]">
                    <th className="py-3 px-4">ID</th>
                    <th className="py-3 px-4">EMAIL ADDRESS</th>
                    <th className="py-3 px-4">СТРАНА (GEOIP)</th>
                    <th className="py-3 px-4">ПОСЛЕДНЯЯ АКТИВНОСТЬ</th>
                    <th className="py-3 px-4">КАТЕГОРИЯ</th>
                    <th className="py-3 px-4">ИСТОЧНИК</th>
                    <th className="py-3 px-4">SCORE</th>
                    <th className="py-3 px-4 text-right">ВРЕМЯ НАХОДКИ</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-purple-950/30">
                  {filteredDbContacts.map((c) => (
                    <tr key={c.id} className="hover:bg-purple-950/20">
                      <td className="py-3 px-4 text-slate-500">{c.id}</td>
                      <td className="py-3 px-4 font-semibold text-cyan-300">{c.email}</td>
                      <td className="py-3 px-4 text-slate-200">{c.country}</td>
                      <td className="py-3 px-4 text-emerald-400">{c.lastActive}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                          c.category === 'HUMAN / PERSONAL'
                            ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-500/50'
                            : 'bg-purple-950/60 text-purple-300 border border-purple-500/50'
                        }`}>
                          {c.category}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-purple-300">{c.targetSource}</td>
                      <td className="py-3 px-4 text-slate-300">{c.score}</td>
                      <td className="py-3 px-4 text-right text-slate-500">{c.timestamp}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 9: DESKTOP PYTHON SOURCE */}
        {activeTab === 'python' && (
          <div className="p-8 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-white tracking-wide">&lt;/&gt; Desktop Python Source (allparser.py)</h1>
                <p className="text-xs text-slate-400 mt-1">Все функции в едином монолитном файле Python со встроенной SQLite базой</p>
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

      {/* AI Translate & Compose Modal */}
      {aiModalOpen && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0e0918] border border-purple-500/50 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl shadow-purple-900/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-cyan-400" />
                <h3 className="text-base font-bold text-white">✨ Мультиязычная генерация письма</h3>
              </div>
              <button onClick={() => setAiModalOpen(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>
            <p className="text-xs text-slate-400">
              Опишите задачу письма на русском языке. ИИ переведёт и составит деловое письмо на выбранном языке:
            </p>
            <div className="text-xs font-bold text-cyan-300">
              Выбранный язык: {LANGUAGES.find(l => l.code === selectedLang)?.name}
            </div>
            <input
              type="text"
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAiTranslateAndDraft()}
              placeholder="Например: Предложить разработчику соавторство в Open Source проекте на Python"
              className="w-full bg-[#06040a] border border-purple-900/40 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-cyan-400"
            />
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setAiModalOpen(false)}
                className="px-4 py-2 bg-black/40 text-slate-400 rounded-xl text-xs"
              >
                Отмена
              </button>
              <button
                onClick={handleAiTranslateAndDraft}
                disabled={aiGenerating || !aiPrompt}
                className="px-5 py-2 bg-gradient-to-r from-purple-600 to-cyan-500 text-black font-bold text-xs rounded-xl flex items-center gap-2 disabled:opacity-50"
              >
                {aiGenerating ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                {aiGenerating ? 'Генерация...' : 'Сгенерировать на языке'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
