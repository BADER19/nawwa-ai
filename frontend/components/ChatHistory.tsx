import React, { useEffect, useState } from 'react';
import api from '../lib/api';

interface ChatMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  visualization_spec?: any;
  interpreter_source?: string;
  created_at: string;
}

interface ChatHistoryProps {
  onSelectMessage?: (message: ChatMessage) => void;
  limit?: number;
}

export default function ChatHistory({ onSelectMessage, limit = 20 }: ChatHistoryProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchChatHistory();
  }, []);

  const fetchChatHistory = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/chat/messages/recent?limit=${limit}`);
      setMessages(response.data);
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch chat history:', err);
      setError(err.response?.data?.detail || 'Failed to load chat history');
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = async () => {
    if (!confirm('Clear all chat history? This cannot be undone.')) return;

    try {
      await api.delete('/chat/messages');
      setMessages([]);
    } catch (err: any) {
      alert('Failed to clear history: ' + (err.response?.data?.detail || 'Unknown error'));
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
        Loading chat history...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px', color: '#ff4444' }}>
        {error}
        <button onClick={fetchChatHistory} style={{ marginLeft: '10px' }}>
          Retry
        </button>
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
        No chat history yet. Start creating visualizations!
      </div>
    );
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div
        style={{
          padding: '15px 20px',
          borderBottom: '1px solid #e0e0e0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>
          Chat History
        </h3>
        <button
          onClick={clearHistory}
          style={{
            padding: '6px 12px',
            fontSize: '12px',
            background: '#ff4444',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Clear All
        </button>
      </div>

      {/* Messages List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '10px' }}>
        {messages.map((message) => (
          <div
            key={message.id}
            onClick={() => onSelectMessage?.(message)}
            style={{
              padding: '12px',
              marginBottom: '8px',
              borderRadius: '8px',
              background: message.role === 'user' ? '#f0f7ff' : '#f5f5f5',
              cursor: onSelectMessage ? 'pointer' : 'default',
              border: '1px solid',
              borderColor: message.role === 'user' ? '#d0e7ff' : '#e0e0e0',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              if (onSelectMessage) {
                e.currentTarget.style.transform = 'translateX(4px)';
                e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
              }
            }}
            onMouseLeave={(e) => {
              if (onSelectMessage) {
                e.currentTarget.style.transform = 'translateX(0)';
                e.currentTarget.style.boxShadow = 'none';
              }
            }}
          >
            {/* Role Badge */}
            <div
              style={{
                display: 'inline-block',
                padding: '2px 8px',
                fontSize: '10px',
                fontWeight: 600,
                textTransform: 'uppercase',
                borderRadius: '4px',
                marginBottom: '6px',
                background: message.role === 'user' ? '#0066cc' : '#666',
                color: 'white',
              }}
            >
              {message.role}
            </div>

            {/* Content */}
            <div
              style={{
                fontSize: '14px',
                lineHeight: '1.5',
                color: '#333',
                marginBottom: '6px',
                maxHeight: '60px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
            >
              {message.content}
            </div>

            {/* Metadata */}
            <div
              style={{
                fontSize: '11px',
                color: '#999',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <span>{formatTime(message.created_at)}</span>
              {message.interpreter_source && (
                <span
                  style={{
                    background: '#e0e0e0',
                    padding: '2px 6px',
                    borderRadius: '3px',
                    fontSize: '10px',
                  }}
                >
                  {message.interpreter_source}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
