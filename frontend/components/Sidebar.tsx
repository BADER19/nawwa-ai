import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { CreditCard, Palette, FolderOpen, User, Settings, LogOut, MessageSquare, Plus, MoreVertical, Trash2, Edit2, Archive } from 'lucide-react';
import { api } from '../lib/api';

export interface ChatSession {
  id: string;
  title: string;
  preview: string;
  timestamp: Date;
  messageCount: number;
  archived?: boolean;
}

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  chatSessions?: ChatSession[];
  currentChatId?: string;
  onSelectChat?: (chatId: string) => void;
  onNewChat?: () => void;
  onDeleteChat?: (chatId: string) => void;
  onRenameChat?: (chatId: string, newTitle: string) => void;
  onArchiveChat?: (chatId: string) => void;
}

export default function Sidebar({ isOpen, onToggle, chatSessions = [], currentChatId, onSelectChat, onNewChat, onDeleteChat, onRenameChat, onArchiveChat }: SidebarProps) {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [workspaceCount, setWorkspaceCount] = useState(0);
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  const [renamingChatId, setRenamingChatId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState('');

  useEffect(() => {
    fetchUserData();
    fetchWorkspaceCount();
  }, []);

  const fetchUserData = async () => {
    try {
      const response = await api.get('/auth/me');
      setUsername(response.data.username);
    } catch (err) {
      console.error('Failed to fetch user data:', err);
    }
  };

  const fetchWorkspaceCount = async () => {
    try {
      const response = await api.get('/workspace/');
      setWorkspaceCount(response.data.length);
    } catch (err) {
      console.error('Failed to fetch workspace count:', err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/auth');
  };

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div
          onClick={onToggle}
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.5)',
            zIndex: 40
          }}
          className="md:hidden"
        />
      )}

      {/* Sidebar */}
      <div style={{
        width: '260px',
        height: '100vh',
        background: '#fcfcfc',
        borderRight: '1px solid #e5e7eb',
        display: 'flex',
        flexDirection: 'column',
        position: 'fixed',
        left: isOpen ? 0 : '-260px',
        top: 0,
        overflowY: 'auto',
        zIndex: 45,
        transition: 'left 0.3s ease',
        boxShadow: isOpen ? '2px 0 8px rgba(0,0,0,0.1)' : 'none'
      }}>
        {/* Logo */}
        <div style={{
          padding: '20px',
          borderBottom: '1px solid #e5e7eb'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            cursor: 'pointer'
          }} onClick={() => router.push('/')}>
            <img
              src="/assets/logo/logo.svg"
              alt="logo"
              style={{ height: '80px', width: '80px', objectFit: 'contain' }}
            />
            <span style={{ fontSize: '16px', fontWeight: 600 }}>Nawwa</span>
          </div>
        </div>

      {/* Chat History Section */}
      <div style={{ padding: '8px 16px 0 16px' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '8px'
        }}>
          <span style={{
            fontSize: '11px',
            fontWeight: 600,
            color: '#9ca3af',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Previous Chats
          </span>
          {onNewChat && (
            <button
              onClick={onNewChat}
              style={{
                padding: '4px 8px',
                background: '#000',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                fontSize: '11px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontWeight: 500
              }}
              onMouseOver={(e) => e.currentTarget.style.background = '#374151'}
              onMouseOut={(e) => e.currentTarget.style.background = '#000'}
            >
              <Plus size={12} />
              New
            </button>
          )}
        </div>

        {/* Chat Sessions List */}
        <div style={{
          maxHeight: '300px',
          overflowY: 'auto',
          marginBottom: '12px'
        }}>
          {chatSessions.length === 0 ? (
            <div style={{
              padding: '16px',
              textAlign: 'center',
              color: '#9ca3af',
              fontSize: '12px'
            }}>
              No chat history yet
            </div>
          ) : (
            chatSessions.map((session, index) => (
              <div
                key={session.id}
                style={{
                  position: 'relative',
                  marginBottom: '4px'
                }}
              >
                <button
                  onClick={() => onSelectChat?.(session.id)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    paddingRight: '36px',
                    background: currentChatId === session.id ? '#f3f4f6' : 'transparent',
                    border: currentChatId === session.id ? '1px solid #d1d5db' : '1px solid transparent',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'all 0.2s'
                  }}
                  onMouseOver={(e) => {
                    if (currentChatId !== session.id) {
                      e.currentTarget.style.background = '#f9fafb';
                    }
                  }}
                  onMouseOut={(e) => {
                    if (currentChatId !== session.id) {
                      e.currentTarget.style.background = 'transparent';
                    }
                  }}
                >
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    marginBottom: '4px'
                  }}>
                    <MessageSquare size={14} strokeWidth={1.5} style={{ color: '#6b7280' }} />
                    {renamingChatId === session.id ? (
                      <input
                        autoFocus
                        value={renameValue}
                        onChange={(e) => setRenameValue(e.target.value)}
                        onBlur={() => {
                          if (renameValue.trim()) {
                            onRenameChat?.(session.id, renameValue);
                          }
                          setRenamingChatId(null);
                        }}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            if (renameValue.trim()) {
                              onRenameChat?.(session.id, renameValue);
                            }
                            setRenamingChatId(null);
                          } else if (e.key === 'Escape') {
                            setRenamingChatId(null);
                          }
                        }}
                        onClick={(e) => e.stopPropagation()}
                        style={{
                          flex: 1,
                          fontSize: '13px',
                          fontWeight: 600,
                          color: '#111827',
                          background: 'white',
                          border: '1px solid #d1d5db',
                          borderRadius: '4px',
                          padding: '2px 4px',
                          outline: 'none'
                        }}
                      />
                    ) : (
                      <span style={{
                        fontSize: '13px',
                        fontWeight: 600,
                        color: '#111827'
                      }}>
                        {session.title || `Chat #${chatSessions.length - index}`}
                      </span>
                    )}
                    <span style={{
                      fontSize: '10px',
                      color: '#9ca3af',
                      marginLeft: 'auto'
                    }}>
                      {session.messageCount} msg{session.messageCount !== 1 ? 's' : ''}
                    </span>
                  </div>
                  <div style={{
                    fontSize: '11px',
                    color: '#6b7280',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis'
                  }}>
                    {session.preview}
                  </div>
                </button>

                {/* Three-dot menu button */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setOpenMenuId(openMenuId === session.id ? null : session.id);
                  }}
                  style={{
                    position: 'absolute',
                    right: '8px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    padding: '4px',
                    background: 'transparent',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'background 0.2s'
                  }}
                  onMouseOver={(e) => e.currentTarget.style.background = '#e5e7eb'}
                  onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
                >
                  <MoreVertical size={16} strokeWidth={1.5} style={{ color: '#6b7280' }} />
                </button>

                {/* Dropdown menu */}
                {openMenuId === session.id && (
                  <div
                    style={{
                      position: 'absolute',
                      right: '8px',
                      top: '100%',
                      marginTop: '4px',
                      background: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                      zIndex: 50,
                      minWidth: '150px',
                      overflow: 'hidden'
                    }}
                  >
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setRenameValue(session.title || `Chat #${chatSessions.length - index}`);
                        setRenamingChatId(session.id);
                        setOpenMenuId(null);
                      }}
                      style={{
                        width: '100%',
                        padding: '10px 12px',
                        background: 'transparent',
                        border: 'none',
                        textAlign: 'left',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '13px',
                        color: '#374151',
                        transition: 'background 0.2s'
                      }}
                      onMouseOver={(e) => e.currentTarget.style.background = '#f9fafb'}
                      onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
                    >
                      <Edit2 size={14} strokeWidth={1.5} />
                      Rename
                    </button>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onArchiveChat?.(session.id);
                        setOpenMenuId(null);
                      }}
                      style={{
                        width: '100%',
                        padding: '10px 12px',
                        background: 'transparent',
                        border: 'none',
                        textAlign: 'left',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '13px',
                        color: '#374151',
                        transition: 'background 0.2s'
                      }}
                      onMouseOver={(e) => e.currentTarget.style.background = '#f9fafb'}
                      onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
                    >
                      <Archive size={14} strokeWidth={1.5} />
                      Archive
                    </button>

                    <div style={{ height: '1px', background: '#e5e7eb', margin: '4px 0' }} />

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm('Are you sure you want to delete this chat? This cannot be undone.')) {
                          onDeleteChat?.(session.id);
                        }
                        setOpenMenuId(null);
                      }}
                      style={{
                        width: '100%',
                        padding: '10px 12px',
                        background: 'transparent',
                        border: 'none',
                        textAlign: 'left',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '13px',
                        color: '#dc2626',
                        transition: 'background 0.2s'
                      }}
                      onMouseOver={(e) => e.currentTarget.style.background = '#fef2f2'}
                      onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
                    >
                      <Trash2 size={14} strokeWidth={1.5} />
                      Delete
                    </button>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: '8px' }}>
        {/* Billing */}
        <SidebarItem
          icon={<CreditCard size={18} strokeWidth={1.5} />}
          label="Billing"
          onClick={() => router.push('/dashboard')}
          active={router.pathname === '/dashboard'}
        />

        {/* Workspace */}
        <SidebarItem
          icon={<Palette size={18} strokeWidth={1.5} />}
          label="Workspace"
          onClick={() => router.push('/app')}
          active={router.pathname === '/app'}
        />

        {/* My Workspaces */}
        <SidebarItem
          icon={<FolderOpen size={18} strokeWidth={1.5} />}
          label="My Workspaces"
          badge={workspaceCount}
          onClick={() => router.push('/workspaces')}
          active={router.pathname === '/workspaces'}
        />

        {/* Divider */}
        <div style={{
          height: '1px',
          background: '#e5e7eb',
          margin: '12px 8px'
        }} />

        {/* Section Title */}
        <div style={{
          padding: '8px 12px',
          fontSize: '11px',
          fontWeight: 600,
          color: '#9ca3af',
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          Account
        </div>

        {/* Profile */}
        <SidebarItem
          icon={<User size={18} strokeWidth={1.5} />}
          label={username || 'Profile'}
          onClick={() => router.push('/profile')}
          active={router.pathname === '/profile'}
        />

        {/* Settings */}
        <SidebarItem
          icon={<Settings size={18} strokeWidth={1.5} />}
          label="Settings"
          onClick={() => router.push('/settings')}
          active={router.pathname === '/settings'}
        />
      </nav>

      {/* Bottom Section */}
      <div style={{
        padding: '16px',
        borderTop: '1px solid #e5e7eb'
      }}>
        <button
          onClick={handleLogout}
          style={{
            width: '100%',
            padding: '10px',
            background: 'transparent',
            color: '#dc2626',
            border: '1px solid #e5e7eb',
            borderRadius: '6px',
            fontSize: '14px',
            fontWeight: 500,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.background = '#fef2f2';
            e.currentTarget.style.borderColor = '#fecaca';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.background = 'transparent';
            e.currentTarget.style.borderColor = '#e5e7eb';
          }}
        >
          <LogOut size={16} strokeWidth={1.5} />
          Logout
        </button>
      </div>
    </div>
    </>
  );
}

interface SidebarItemProps {
  icon: React.ReactNode;
  label: string;
  badge?: number;
  onClick: () => void;
  active?: boolean;
}

function SidebarItem({ icon, label, badge, onClick, active }: SidebarItemProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        width: '100%',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        padding: '10px 12px',
        background: active ? '#f3f4f6' : isHovered ? '#f9fafb' : 'transparent',
        border: 'none',
        borderRadius: '6px',
        cursor: 'pointer',
        marginBottom: '4px',
        transition: 'background 0.2s'
      }}
    >
      <span style={{ display: 'flex', alignItems: 'center', color: active ? '#000' : '#6b7280' }}>{icon}</span>
      <span style={{
        flex: 1,
        textAlign: 'left',
        fontSize: '14px',
        fontWeight: active ? 600 : 400,
        color: active ? '#000' : '#374151'
      }}>
        {label}
      </span>
      {badge !== undefined && badge > 0 && (
        <span style={{
          padding: '2px 8px',
          background: '#e5e7eb',
          color: '#374151',
          fontSize: '12px',
          fontWeight: 600,
          borderRadius: '12px'
        }}>
          {badge}
        </span>
      )}
    </button>
  );
}
