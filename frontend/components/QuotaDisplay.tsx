import { useEffect, useState } from 'react';
import { Sparkles } from 'lucide-react';

interface QuotaDisplayProps {
  used: number;
  limit: number;
  onUpgradeClick?: () => void;
}

export default function QuotaDisplay({ used, limit, onUpgradeClick }: QuotaDisplayProps) {
  const [prevUsed, setPrevUsed] = useState(used);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (used !== prevUsed) {
      setIsAnimating(true);
      setPrevUsed(used);
      setTimeout(() => setIsAnimating(false), 600);
    }
  }, [used, prevUsed]);

  // Handle unlimited quota (-1)
  if (limit === -1) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 rounded-lg border bg-purple-50 border-purple-200">
        <Sparkles size={16} className="text-purple-500" />
        <span className="text-xs font-medium text-purple-700">
          Unlimited AI requests
        </span>
      </div>
    );
  }

  const remaining = Math.max(0, limit - used);
  const percentage = limit > 0 ? (remaining / limit) * 100 : 0;

  // Color scheme based on remaining quota
  const getColorScheme = () => {
    if (percentage >= 60) {
      return {
        bg: 'bg-emerald-50',
        border: 'border-emerald-200',
        text: 'text-emerald-700',
        bar: 'bg-emerald-500',
        glow: 'shadow-emerald-200/50',
        icon: 'text-emerald-500'
      };
    } else if (percentage >= 30) {
      return {
        bg: 'bg-amber-50',
        border: 'border-amber-200',
        text: 'text-amber-700',
        bar: 'bg-amber-500',
        glow: 'shadow-amber-200/50',
        icon: 'text-amber-500'
      };
    } else {
      return {
        bg: 'bg-rose-50',
        border: 'border-rose-200',
        text: 'text-rose-700',
        bar: 'bg-rose-500',
        glow: 'shadow-rose-200/50',
        icon: 'text-rose-500'
      };
    }
  };

  const colors = getColorScheme();

  return (
    <div className={`flex items-center gap-3 px-3 py-2 rounded-lg border ${colors.bg} ${colors.border} transition-all duration-500 ${isAnimating ? `scale-105 shadow-lg ${colors.glow}` : ''}`}>
      {/* Icon */}
      <Sparkles
        size={16}
        className={`${colors.icon} transition-all duration-500 ${isAnimating ? 'rotate-180' : ''}`}
      />

      {/* Text and Progress */}
      <div className="flex flex-col gap-1 min-w-[140px]">
        <div className="flex items-center justify-between">
          <span className={`text-xs font-medium ${colors.text} transition-colors duration-500`}>
            {remaining === 0 ? (
              'Daily limit reached'
            ) : (
              <>
                <span className={`font-bold text-sm ${isAnimating ? 'animate-pulse' : ''}`}>
                  {remaining}
                </span>
                <span className="opacity-70"> / {limit} AI requests</span>
              </>
            )}
          </span>
        </div>

        {/* Progress Bar */}
        <div className="relative w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`absolute inset-y-0 left-0 ${colors.bar} rounded-full transition-all duration-700 ease-out`}
            style={{ width: `${percentage}%` }}
          />
          {isAnimating && (
            <div
              className="absolute inset-y-0 left-0 bg-white/40 rounded-full animate-pulse"
              style={{ width: `${percentage}%` }}
            />
          )}
        </div>
      </div>

      {/* Upgrade CTA - Only show when quota is low or exhausted */}
      {percentage < 30 && onUpgradeClick && (
        <button
          onClick={onUpgradeClick}
          className="px-2.5 py-1 text-xs font-medium bg-black text-white rounded-md hover:bg-gray-800 transition-all duration-200 hover:shadow-md active:scale-95 whitespace-nowrap"
        >
          Upgrade
        </button>
      )}
    </div>
  );
}
