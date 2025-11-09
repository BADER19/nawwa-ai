import { useEffect, useRef, useState, KeyboardEvent } from 'react';
import VoiceInput from './VoiceInput';

type Props = {
  initial?: string;
  onSubmit: (command: string) => void;
  onVoiceResult?: (transcription: string, visualization: any) => void;
  placeholder?: string;
  hideScrollbar?: boolean;
  voiceEnabled?: boolean;
};

export default function ChatInput({ initial = '', onSubmit, onVoiceResult, placeholder = 'Ask anything', hideScrollbar = false, voiceEnabled = false }: Props) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const composingRef = useRef(false);
  const [value, setValue] = useState(initial);
  const [maxRows, setMaxRows] = useState(6);

  // Desktop vs mobile caps
  useEffect(() => {
    const checkScreenSize = () => {
      const isDesktop = window.matchMedia('(min-width: 768px)').matches;
      setMaxRows(isDesktop ? 8 : 6);
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  const resize = () => {
    const el = textareaRef.current;
    if (!el) return;
    // rAF avoids layout thrash/flicker when typing/pasting quickly
    requestAnimationFrame(() => {
      el.style.height = 'auto';
      // Use pixel line-height so maxRows is deterministic
      const lineHeight = parseFloat(getComputedStyle(el).lineHeight || '20');
      const maxHeight = lineHeight * maxRows;
      const next = Math.min(el.scrollHeight, maxHeight);
      el.style.height = `${next}px`;

      // Only show scrollbar when content exceeds maxHeight
      if (el.scrollHeight > maxHeight) {
        el.style.overflowY = hideScrollbar ? 'hidden' : 'auto';
      } else {
        el.style.overflowY = 'hidden';
      }

      // Keep caret visible after large paste
      el.scrollTop = el.scrollHeight;
    });
  };

  useEffect(() => {
    resize();
  }, [value, maxRows]);

  useEffect(() => {
    resize(); // initial
    const el = textareaRef.current;
    const ro = new ResizeObserver(resize);
    el && ro.observe(el);

    const onWin = () => resize();
    window.addEventListener('resize', onWin);
    return () => {
      ro.disconnect();
      window.removeEventListener('resize', onWin);
    };
  }, []);

  const handleSubmit = () => {
    const msg = value.trim();
    if (!msg) return;
    onSubmit(msg);
    setValue('');
  };

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (composingRef.current) return; // IME safety
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const hasText = value.trim().length > 0;

  return (
    <div
      className={[
        'flex items-center w-full bg-white border border-gray-200 rounded-full shadow-sm',
        'px-3 py-2 min-h-[56px]',
        'transition-all duration-150',
        'hover:shadow-md focus-within:shadow-md focus-within:border-gray-300 focus-within:ring-1 focus-within:ring-gray-300',
      ].join(' ')}
    >
      {/* Left + */}
      <button
        type="button"
        className="shrink-0 grid place-items-center w-9 h-9 border border-gray-300 rounded-full text-gray-900 text-xl hover:bg-gray-50 active:scale-[0.98] transition"
        aria-label="Add"
      >
        +
      </button>

      {/* Textarea */}
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={onKeyDown}
        onCompositionStart={() => (composingRef.current = true)}
        onCompositionEnd={() => (composingRef.current = false)}
        rows={1}
        placeholder={placeholder}
        spellCheck
        autoCapitalize="off"
        autoCorrect="off"
        aria-label="Message"
        className={[
          'flex-1 mx-3 resize-none bg-transparent outline-none border-0',
          'text-gray-800 placeholder:text-gray-400',
          'text-[15px] leading-[20px]',
          'py-[6px]',
          'min-h-[22px] max-h-[40vh] overflow-y-hidden',
          hideScrollbar && '[scrollbar-width:none] [&::-webkit-scrollbar]:hidden',
        ].filter(Boolean).join(' ')}
      />

      {/* Right actions */}
      <div className="shrink-0">
        {hasText ? (
          <button
            type="button"
            onClick={handleSubmit}
            className="grid place-items-center w-9 h-9 rounded-full bg-black text-white hover:bg-gray-800 active:scale-[0.98] transition"
            aria-label="Send"
            title="Send"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 5l7 7-7 7" />
              <path d="M21 12H3" />
            </svg>
          </button>
        ) : (
          <div className="h-9 rounded-full bg-gray-100 px-2 flex items-center gap-2">
            <VoiceInput
              onTranscription={(transcription, visualization) => {
                // Pass the visualization result directly without setting input value
                // The visualization is already processed, no need to fill the input
                if (onVoiceResult) {
                  onVoiceResult(transcription, visualization);
                }
              }}
              tierAllowed={voiceEnabled}
            />
          </div>
        )}
      </div>
    </div>
  );
}

