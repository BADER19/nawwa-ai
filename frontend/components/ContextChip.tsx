import { useState, useEffect, useRef } from 'react';
import { api } from '../lib/api';

type Props = {
  userContext: string;
  onContextUpdate: (context: string) => void;
};

export default function ContextChip({ userContext, onContextUpdate }: Props) {
  const [isOpen, setIsOpen] = useState(false);
  const [draftText, setDraftText] = useState(userContext);
  const [isSaving, setIsSaving] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setDraftText(userContext);
  }, [userContext]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setDraftText(userContext); // Reset on close
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, userContext]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await api.put('/auth/me/context', { current_context: draftText.trim() });
      onContextUpdate(draftText.trim());
      setIsOpen(false);
    } catch (err) {
      console.error('Failed to save context:', err);
      alert('Failed to save context');
    } finally {
      setIsSaving(false);
    }
  };

  const handleClear = async () => {
    setIsSaving(true);
    try {
      await api.put('/auth/me/context', { current_context: '' });
      onContextUpdate('');
      setDraftText('');
      setIsOpen(false);
    } catch (err) {
      console.error('Failed to clear context:', err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div ref={dropdownRef} style={{ position: 'relative' }}>
      {/* Context Chip Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="px-3 py-1.5 text-xs bg-gray-100 hover:bg-gray-200 rounded-full transition-colors flex items-center gap-2"
        title="Set your work context"
      >
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z" />
          <path d="M2 17l10 5 10-5" />
          <path d="M2 12l10 5 10-5" />
        </svg>
        <span className="text-gray-700">
          {userContext ? userContext.substring(0, 20) + (userContext.length > 20 ? '...' : '') : 'Context'}
        </span>
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div
          className="absolute top-full left-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg p-3 z-50"
          style={{ width: '320px' }}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-600 uppercase">My Context</span>
            <button
              onClick={() => {
                setIsOpen(false);
                setDraftText(userContext);
              }}
              className="text-gray-400 hover:text-gray-600"
            >
              ×
            </button>
          </div>

          <textarea
            autoFocus
            value={draftText}
            onChange={(e) => setDraftText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (!isSaving) {
                  handleSave();
                }
              }
            }}
            placeholder="e.g., Teaching high school students (optional)"
            className="w-full p-2 text-xs border border-gray-300 rounded resize-none outline-none focus:border-black"
            style={{ minHeight: '60px' }}
          />

          <div className="text-xs text-gray-500 mt-1 mb-2">
            Press <strong>Enter</strong> to save • Leave blank to disable context
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex-1 px-3 py-1.5 text-xs bg-black text-white rounded hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isSaving ? 'Saving...' : 'Save'}
            </button>
            {userContext && (
              <button
                onClick={handleClear}
                disabled={isSaving}
                className="px-3 py-1.5 text-xs text-red-600 border border-red-300 rounded hover:bg-red-50 disabled:opacity-50 transition-colors"
                title="Clear context"
              >
                Clear
              </button>
            )}
            <button
              onClick={() => {
                setDraftText(userContext);
                setIsOpen(false);
              }}
              className="px-3 py-1.5 text-xs text-gray-600 border border-gray-300 rounded hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
