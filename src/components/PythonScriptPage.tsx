import React, { useState, useEffect } from 'react';
import { Code2, Download, Copy, Check, Terminal, Sparkles, ShieldCheck, Play } from 'lucide-react';
import { RainbowLine } from './RainbowLine';

export const PythonScriptPage: React.FC = () => {
  const [copied, setCopied] = useState<boolean>(false);
  const [scriptContent, setScriptContent] = useState<string>('Loading complete script...');

  useEffect(() => {
    fetch('/api/python-script')
      .then(r => r.text())
      .then(text => setScriptContent(text))
      .catch(() => {
        setScriptContent('# Error loading morphh_v2.py');
      });
  }, []);

  const handleCopy = () => {
    navigator.clipboard.writeText(scriptContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([scriptContent], { type: 'text/x-python;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'morphh_v2.py';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-extrabold text-white tracking-wider flex items-center gap-3">
              <Code2 className="w-7 h-7 text-[#00f3ff]" />
              <span>Единый Код Python Desktop (morphh_v2.py)</span>
            </h2>
            <p className="text-xs text-[#8a8aa0] mt-1 font-mono">
              Весь проект соединён в один цельный файл: Spider, Dorks, Gemini AI, accounts.txt, Lo-Fi Radio и GUI PyQt6
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleCopy}
              className="px-4 py-2 rounded-xl bg-[#8a2be2]/20 hover:bg-[#8a2be2]/30 text-[#c084fc] font-mono text-xs font-bold flex items-center gap-2 border border-[#8a2be2]/30"
            >
              {copied ? <Check className="w-4 h-4 text-[#00ff9d]" /> : <Copy className="w-4 h-4" />}
              <span>{copied ? 'Скопировано!' : 'Копировать Весь Код'}</span>
            </button>

            <button
              onClick={handleDownload}
              className="px-5 py-2 rounded-xl bg-[#00f3ff]/20 hover:bg-[#00f3ff]/30 text-[#00f3ff] font-mono text-xs font-bold flex items-center gap-2 border border-[#00f3ff]/40 shadow-[0_0_15px_rgba(0,243,255,0.2)]"
            >
              <Download className="w-4 h-4" />
              <span>Скачать morphh_v2.py</span>
            </button>
          </div>
        </div>
        <RainbowLine className="mt-4" />
      </div>

      {/* Guide Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-panel p-4 rounded-xl border border-[#00f3ff]/30 space-y-1">
          <div className="flex items-center gap-2 text-[#00f3ff] font-mono text-xs font-bold">
            <Play className="w-4 h-4" />
            <span>1. В Web-Интерфейсе (Здесь)</span>
          </div>
          <p className="text-[11px] text-[#8a8aa0] font-mono leading-relaxed">
            Всё уже соединено и работает прямо в этом окне! Перейдите на вкладку <strong>Spider & Dorks</strong> и нажмите &quot;Запустить&quot;.
          </p>
        </div>

        <div className="glass-panel p-4 rounded-xl border border-[#00ff9d]/30 space-y-1">
          <div className="flex items-center gap-2 text-[#00ff9d] font-mono text-xs font-bold">
            <Terminal className="w-4 h-4" />
            <span>2. Локально на ПК (Python)</span>
          </div>
          <p className="text-[11px] text-[#8a8aa0] font-mono leading-relaxed">
            Сохраните код в файл <code>morphh_v2.py</code> и запустите в терминале: <br />
            <code className="text-[#00ff9d]">python morphh_v2.py</code>
          </p>
        </div>

        <div className="glass-panel p-4 rounded-xl border border-[#ffcc00]/30 space-y-1">
          <div className="flex items-center gap-2 text-[#ffcc00] font-mono text-xs font-bold">
            <ShieldCheck className="w-4 h-4" />
            <span>3. Авто-файлы</span>
          </div>
          <p className="text-[11px] text-[#8a8aa0] font-mono leading-relaxed">
            Скрипт сам создаст <code>accounts.txt</code>, <code>BazaPochtRassilka.txt</code> и установит PyQt6 и requests без ошибок.
          </p>
        </div>
      </div>

      {/* Code Viewer */}
      <div className="glass-panel p-5 rounded-2xl border border-[#8a2be2]/30 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-[#00f3ff] font-bold uppercase">
            Цельный исполняемый скрипт (morphh_v2.py)
          </span>
          <span className="text-[11px] font-mono text-[#6a6a80]">
            Python 3.10+ / PyQt6
          </span>
        </div>

        <pre className="h-[520px] overflow-auto rounded-xl bg-[#050508]/95 border border-[#8a2be2]/25 p-4 font-mono text-xs text-[#00ff9d] leading-relaxed">
          <code>{scriptContent}</code>
        </pre>
      </div>
    </div>
  );
};
