import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { Menu } from 'lucide-react';
import VisualizationRouter from '../components/VisualizationRouter';
import ChatInput from '../components/ChatInput';
import Sidebar, { ChatSession } from '../components/Sidebar';
import QuotaDisplay from '../components/QuotaDisplay';
import ContextChip from '../components/ContextChip';
import { apiGet, apiPost, apiPostWithHeaders } from '../lib/api';

type VisualSpec = {
  visualType?: 'conceptual' | 'mathematical' | 'mathematical_interactive' | 'timeline' | 'statistical' | 'mermaid' | 'plotly';
  elements?: Array<{
    type: string;
    x?: number; y?: number;
    radius?: number; width?: number; height?: number;
    color?: string;
    [key: string]: any;
  }>;
  expression?: string;
  expressions?: string[];
  mermaidCode?: string;
  nodes?: Array<{id: string; label: string; [key: string]: any}>;
  links?: Array<{source: string; target: string; [key: string]: any}>;
  plotlySpec?: {
    data: any[];
    layout?: any;
    config?: any;
  };
};

type Workspace = {
  id: number;
  name: string;
  data: VisualSpec;
  created_at?: string;
};

type ChatMessage = {
  id: string;
  prompt: string;
  visualization: VisualSpec;
  timestamp: Date;
};

export default function AppPage() {
  const router = useRouter();
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [allChatSessions, setAllChatSessions] = useState<Map<string, ChatMessage[]>>(new Map());
  const [currentChatId, setCurrentChatId] = useState<string>('');
  const [name, setName] = useState('New Workspace');
  const [savedId, setSavedId] = useState<number | null>(null);
  const [msg, setMsg] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [userContext, setUserContext] = useState<string>('');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [quotaUsed, setQuotaUsed] = useState(0);
  const [quotaLimit, setQuotaLimit] = useState(20); // Default to FREE tier limit
  const [voiceEnabled, setVoiceEnabled] = useState(false); // Voice input enabled for PRO+ tiers

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const token = localStorage.getItem('token');
    if (!token) router.replace('/auth');
    else {
      // Initialize first chat session
      const initialChatId = `chat-${Date.now()}`;
      setCurrentChatId(initialChatId);

      // Load chat sessions from localStorage
      const savedSessions = localStorage.getItem('chat_sessions');
      if (savedSessions) {
        try {
          const parsed = JSON.parse(savedSessions);
          const sessionsMap = new Map();

          // Convert timestamp strings back to Date objects
          Object.entries(parsed).forEach(([chatId, messages]: [string, any]) => {
            const messagesWithDates = messages.map((msg: any) => ({
              ...msg,
              timestamp: new Date(msg.timestamp)
            }));
            sessionsMap.set(chatId, messagesWithDates);
          });

          setAllChatSessions(sessionsMap);
        } catch (e) {
          console.error('Failed to load chat sessions', e);
        }
      }

      fetchQuotaInfo(); // Fetch initial quota
    }
  }, [router]);

  // Save chat sessions to localStorage whenever they change
  useEffect(() => {
    if (allChatSessions.size > 0) {
      const sessionsObj = Object.fromEntries(allChatSessions);
      localStorage.setItem('chat_sessions', JSON.stringify(sessionsObj));
    }
  }, [allChatSessions]);

  const fetchQuotaInfo = async () => {
    try {
      const data = await apiGet<{
        usage_count: number;
        usage_limit: number | string;
        tier: string;
        features?: string[];
      }>('/subscription/subscription-info');

      setQuotaUsed(data.usage_count);

      // Handle "unlimited" or numeric limit
      if (typeof data.usage_limit === 'string' && data.usage_limit === 'unlimited') {
        setQuotaLimit(-1); // -1 represents unlimited
      } else if (typeof data.usage_limit === 'number') {
        setQuotaLimit(data.usage_limit);
      }

      // Check if voice is enabled for this tier (PRO+)
      const voiceTiers = ['PRO', 'TEAM', 'ENTERPRISE'];
      setVoiceEnabled(voiceTiers.includes(data.tier));
    } catch (e) {
      console.error('Failed to fetch quota info:', e);
      // Keep defaults if fetch fails
    }
  };

  // Dynamic spacer sizing to prevent content from being hidden under fixed input
  useEffect(() => {
    const inputRootId = 'chat-input-root';
    const spacerId = 'input-spacer';

    const sizeSpacer = () => {
      const inputRoot = document.getElementById(inputRootId);
      const spacer = document.getElementById(spacerId);
      if (!inputRoot || !spacer) return;

      // Use requestAnimationFrame for smooth updates
      requestAnimationFrame(() => {
        const rect = inputRoot.getBoundingClientRect();
        spacer.style.height = `${rect.height}px`;
      });
    };

    // Initial sizing
    sizeSpacer();

    // Watch for input root size changes
    const inputRoot = document.getElementById(inputRootId);
    const observer = new ResizeObserver(sizeSpacer);
    if (inputRoot) observer.observe(inputRoot);

    // Also watch window resize
    window.addEventListener('resize', sizeSpacer);

    return () => {
      observer.disconnect();
      window.removeEventListener('resize', sizeSpacer);
    };
  }, []);

  const visualize = async (cmd: string) => {
    setIsLoading(true);
    setMsg('');
    try {
      const { data, usageCount } = await apiPostWithHeaders<VisualSpec>('/visualize/', {
        command: cmd,
        user_context: userContext // Pass user context to AI
      });

      // Add to chat history
      const newMessage: ChatMessage = {
        id: Date.now().toString(),
        prompt: cmd,
        visualization: data,
        timestamp: new Date()
      };
      const updatedHistory = [...chatHistory, newMessage];
      setChatHistory(updatedHistory);

      // Save to all sessions
      setAllChatSessions(prev => {
        const newSessions = new Map(prev);
        newSessions.set(currentChatId, updatedHistory);
        return newSessions;
      });

      setMsg('');

      // Update quota if returned in headers
      if (usageCount !== undefined) {
        setQuotaUsed(usageCount);
      }
    } catch (e: any) {
      const status = e?.response?.status;
      if (status === 429) {
        setMsg('Daily AI quota exceeded. Upgrade to PRO for unlimited visualizations!');
      } else {
        setMsg('AI visualization failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const newChat = () => {
    // Save current chat to sessions if it has messages
    if (chatHistory.length > 0) {
      setAllChatSessions(prev => {
        const newSessions = new Map(prev);
        newSessions.set(currentChatId, chatHistory);
        return newSessions;
      });
    }

    // Create new chat
    const newChatId = `chat-${Date.now()}`;
    setCurrentChatId(newChatId);
    setChatHistory([]);
    setMsg('');
    setSavedId(null);
  };

  const selectChat = (chatId: string) => {
    // Save current chat before switching
    if (chatHistory.length > 0) {
      setAllChatSessions(prev => {
        const newSessions = new Map(prev);
        newSessions.set(currentChatId, chatHistory);
        return newSessions;
      });
    }

    // Load selected chat
    const selectedMessages = allChatSessions.get(chatId) || [];
    setChatHistory(selectedMessages);
    setCurrentChatId(chatId);
  };

  const deleteChat = (chatId: string) => {
    setAllChatSessions(prev => {
      const newSessions = new Map(prev);
      newSessions.delete(chatId);
      return newSessions;
    });

    // If deleting current chat, switch to a new one
    if (chatId === currentChatId) {
      newChat();
    }
  };

  const renameChat = (chatId: string, newTitle: string) => {
    if (typeof window === 'undefined') return;
    // Store custom titles separately in localStorage
    const customTitles = JSON.parse(localStorage.getItem('chat_titles') || '{}');
    customTitles[chatId] = newTitle;
    localStorage.setItem('chat_titles', JSON.stringify(customTitles));
  };

  const archiveChat = (chatId: string) => {
    if (typeof window === 'undefined') return;
    // Store archived chats separately
    const archived = JSON.parse(localStorage.getItem('archived_chats') || '[]');
    if (!archived.includes(chatId)) {
      archived.push(chatId);
      localStorage.setItem('archived_chats', JSON.stringify(archived));
    }

    // If archiving current chat, switch to a new one
    if (chatId === currentChatId) {
      newChat();
    }
  };

  // Convert sessions map to ChatSession array for sidebar
  const getChatSessions = (): ChatSession[] => {
    const sessions: ChatSession[] = [];

    // Only access localStorage in the browser
    const customTitles = typeof window !== 'undefined'
      ? JSON.parse(localStorage.getItem('chat_titles') || '{}')
      : {};
    const archivedChats = typeof window !== 'undefined'
      ? JSON.parse(localStorage.getItem('archived_chats') || '[]')
      : [];

    allChatSessions.forEach((messages, id) => {
      // Skip archived chats
      if (archivedChats.includes(id)) return;

      if (messages.length > 0) {
        const firstMessage = messages[0];
        const timestamp = firstMessage.timestamp instanceof Date
          ? firstMessage.timestamp
          : new Date(firstMessage.timestamp);

        sessions.push({
          id,
          title: customTitles[id] || '',
          preview: firstMessage.prompt.substring(0, 50),
          timestamp,
          messageCount: messages.length
        });
      }
    });

    // Sort by timestamp, newest first
    return sessions.sort((a, b) => {
      const aTime = a.timestamp instanceof Date ? a.timestamp.getTime() : new Date(a.timestamp).getTime();
      const bTime = b.timestamp instanceof Date ? b.timestamp.getTime() : new Date(b.timestamp).getTime();
      return bTime - aTime;
    });
  };

  const save = async () => {
    // Save the latest visualization from chat history
    const latestViz = chatHistory[chatHistory.length - 1]?.visualization || {};
    try {
      const data = await apiPost<{ id: number }>('/workspace/save', { name, data: latestViz });
      setSavedId(data.id);
      if (typeof window !== 'undefined') localStorage.setItem('last_workspace_id', String(data.id));
      setMsg('Saved!');
      setTimeout(() => setMsg(''), 2000);
    } catch {
      setMsg('Failed to save.');
    }
  };

  const loadWorkspace = async (id: number) => {
    try {
      const ws = await apiGet<Workspace>(`/workspace/${id}`);
      // Load workspace as a chat message
      const loadedMessage: ChatMessage = {
        id: Date.now().toString(),
        prompt: ws.name || 'Loaded workspace',
        visualization: ws.data,
        timestamp: new Date(ws.created_at || Date.now())
      };
      setChatHistory([loadedMessage]);
      setSavedId(ws.id);
      setName(ws.name || 'My Workspace');
      if (typeof window !== 'undefined') localStorage.setItem('last_workspace_id', String(id));
    } catch (e) {
      setMsg('Failed to load workspace.');
    }
  };

  const loadLast = async () => {
    if (typeof window === 'undefined') return;
    const idStr = localStorage.getItem('last_workspace_id');
    if (!idStr) return;
    try {
      const ws = await apiGet<Workspace>(`/workspace/${idStr}`);
      const loadedMessage: ChatMessage = {
        id: Date.now().toString(),
        prompt: ws.name || 'Loaded workspace',
        visualization: ws.data,
        timestamp: new Date(ws.created_at || Date.now())
      };
      setChatHistory([loadedMessage]);
      setSavedId(ws.id);
      setName(ws.name || 'My Workspace');
    } catch (e) {
      // Workspace not found
    }
  };

  const exportVisualization = async () => {
    // Export the latest visualization
    const latestViz = chatHistory[chatHistory.length - 1]?.visualization || {};
    try {
      await navigator.clipboard.writeText(JSON.stringify(latestViz, null, 2));
      setMsg('Visualization spec copied to clipboard! You can save and reuse it.');
      setTimeout(() => setMsg(''), 3000);
    } catch (err) {
      setMsg('Failed to export visualization');
    }
  };

  const hasVisualization = chatHistory.length > 0;

  return (
    <div className="flex h-dvh bg-white overflow-hidden">
      {/* Left Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        chatSessions={getChatSessions()}
        currentChatId={currentChatId}
        onSelectChat={selectChat}
        onNewChat={newChat}
        onDeleteChat={deleteChat}
        onRenameChat={renameChat}
        onArchiveChat={archiveChat}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col" style={{
        marginLeft: sidebarOpen ? '260px' : '0',
        transition: 'margin-left 0.3s ease'
      }}>
        {/* Header */}
        <header className="h-14 border-b border-gray-200 bg-white flex items-center justify-between px-4 shrink-0" style={{ zIndex: 30 }}>
          <div className="flex items-center gap-3">
            {/* Hamburger Toggle Button */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="w-10 h-10 flex items-center justify-center rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
              aria-label="Toggle sidebar"
            >
              <Menu size={18} strokeWidth={1.5} />
            </button>
            <h1 className="text-lg font-semibold">Workspace</h1>

            {/* Context Chip - Moved from sidebar */}
            <ContextChip
              userContext={userContext}
              onContextUpdate={setUserContext}
            />
          </div>
          <div className="flex items-center gap-3">
            {/* Quota Display */}
            <QuotaDisplay
              used={quotaUsed}
              limit={quotaLimit}
              onUpgradeClick={() => router.push('/pricing')}
            />
            <div className="flex items-center gap-2">
              <button
                onClick={newChat}
                className="px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-all duration-200 hover:shadow-sm active:scale-95"
              >
                New Chat
              </button>
              <button
                onClick={save}
                disabled={!hasVisualization}
                className="px-3 py-1.5 text-sm bg-black text-white rounded-lg hover:bg-gray-800 hover:shadow-md disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-200 active:scale-95"
              >
                Save
              </button>
              <button
                onClick={exportVisualization}
                disabled={!hasVisualization}
                className="px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-all duration-200 hover:shadow-sm disabled:opacity-30 disabled:cursor-not-allowed active:scale-95"
              >
                Export
              </button>
            </div>
          </div>
        </header>

        {/* Canvas Area - Scrollable */}
        <div className="flex-1 overflow-y-auto">
          <div className="mx-auto w-full max-w-[900px] px-4 pt-4 pb-4">
            {msg && (
              <div className={`mb-4 p-3 rounded-lg text-sm ${msg.includes('failed') || msg.includes('Failed') ? 'bg-red-50 text-red-800' : 'bg-green-50 text-green-800'}`}>
                {msg}
              </div>
            )}

            {!hasVisualization && !isLoading ? (
              <div className="flex flex-col items-center justify-center h-96 text-center">
                <svg className="w-16 h-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <h2 className="text-xl font-medium text-gray-900 mb-2">No visualization yet</h2>
                <p className="text-gray-500 text-sm mb-6 max-w-md">
                  Type a prompt below to create your first visualization
                </p>
                <div className="flex flex-wrap gap-2 justify-center max-w-2xl">
                  {["Plot sin(x)", "Explain photosynthesis", "Timeline of WW2", "Compare democracy vs autocracy"].map((prompt) => (
                    <button
                      key={prompt}
                      onClick={() => visualize(prompt)}
                      className="px-3 py-1.5 text-xs bg-gray-100 hover:bg-gray-200 rounded-lg transition-all duration-200 hover:shadow-sm active:scale-95"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Render all chat messages */}
                {chatHistory.map((message) => (
                  <div key={message.id} className="space-y-4 animate-fade-in">
                    {/* User's prompt */}
                    <div className="flex justify-end">
                      <div className="bg-black text-white px-4 py-2.5 rounded-2xl max-w-[85%]">
                        <p className="text-sm whitespace-pre-wrap">{message.prompt}</p>
                      </div>
                    </div>

                    {/* Visualization response */}
                    <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
                      <VisualizationRouter spec={message.visualization} />
                    </div>
                  </div>
                ))}

                {/* Loading indicator for new message */}
                {isLoading && (
                  <div className="flex items-center justify-center py-8">
                    <div className="text-center">
                      <div className="inline-block animate-spin rounded-full h-10 w-10 border-b-2 border-black mb-3"></div>
                      <p className="text-gray-600 text-sm">Creating visualization...</p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Spacer to prevent content from being hidden under fixed input */}
            <div id="input-spacer" style={{ height: '80px' }} />
          </div>
        </div>

        {/* Chat Input Area - Fixed at bottom */}
        <div
          id="chat-input-root"
          className="fixed right-0 bottom-0 z-40 bg-gradient-to-t from-white via-white/90 to-transparent transition-all duration-300 ease-in-out"
          style={{
            paddingBottom: 'env(safe-area-inset-bottom)',
            left: sidebarOpen ? '260px' : '0',
            transition: 'left 0.3s ease'
          }}
        >
          <div className="mx-auto w-full max-w-[980px] px-4 py-3">
            <ChatInput
              onSubmit={visualize}
              onVoiceResult={(transcription, visualization) => {
                // Add voice result to chat history
                const newMessage: ChatMessage = {
                  id: Date.now().toString(),
                  prompt: transcription,
                  visualization: visualization,
                  timestamp: new Date()
                };
                const updatedHistory = [...chatHistory, newMessage];
                setChatHistory(updatedHistory);

                // Save to all sessions
                setAllChatSessions(prev => {
                  const newSessions = new Map(prev);
                  newSessions.set(currentChatId, updatedHistory);
                  return newSessions;
                });

                setQuotaUsed(prev => prev + 1); // Increment displayed quota
              }}
              hideScrollbar={false}
              voiceEnabled={voiceEnabled}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
