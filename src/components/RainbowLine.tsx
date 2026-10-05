import React from 'react';

export const RainbowLine: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div
      className={`h-[2px] w-full bg-gradient-to-r from-[#8a2be2] via-[#00f3ff] to-[#00ff9d] opacity-80 ${className}`}
    />
  );
};

export const PulseDot: React.FC<{ color?: 'green' | 'cyan' | 'purple' | 'red' | 'amber'; active?: boolean }> = ({
  color = 'green',
  active = true,
}) => {
  const colorMap = {
    green: 'bg-[#00ff9d] shadow-[0_0_8px_#00ff9d]',
    cyan: 'bg-[#00f3ff] shadow-[0_0_8px_#00f3ff]',
    purple: 'bg-[#8a2be2] shadow-[0_0_8px_#8a2be2]',
    red: 'bg-[#ff2a6d] shadow-[0_0_8px_#ff2a6d]',
    amber: 'bg-[#ffcc00] shadow-[0_0_8px_#ffcc00]',
  };

  return (
    <span className="relative flex h-2.5 w-2.5">
      {active && (
        <span
          className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${colorMap[color]}`}
        />
      )}
      <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${colorMap[color]}`} />
    </span>
  );
};
