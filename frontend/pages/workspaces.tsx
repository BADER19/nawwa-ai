import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { FolderOpen, Clock, Trash2, Eye } from 'lucide-react';
import Sidebar from '../components/Sidebar';
import { api } from '../lib/api';

interface Workspace {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
  data: any;
}

export default function WorkspacesPage() {
  const router = useRouter();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.replace('/auth');
      return;
    }
    fetchWorkspaces();
  }, [router]);

  const fetchWorkspaces = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/workspace/');
      setWorkspaces(response.data);
    } catch (err: any) {
      console.error('Failed to fetch workspaces:', err);
      const errorMsg = err.response?.data?.detail;
      // Handle case where detail might be an object (validation error)
      setError(typeof errorMsg === 'string' ? errorMsg : 'Failed to load workspaces');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadWorkspace = (id: number) => {
    localStorage.setItem('last_workspace_id', String(id));
    router.push('/app');
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />

      <div
        className="flex-1 flex flex-col overflow-hidden"
        style={{
          marginLeft: sidebarOpen ? '260px' : '0',
          transition: 'margin-left 0.3s ease'
        }}
      >
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">My Workspaces</h1>
              <p className="text-sm text-gray-600 mt-1">
                {workspaces.length} saved {workspaces.length === 1 ? 'workspace' : 'workspaces'}
              </p>
            </div>
            <button
              onClick={() => router.push('/app')}
              className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors text-sm font-medium"
            >
              Create New
            </button>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center h-96">
              <div className="text-center">
                <div className="inline-block animate-spin rounded-full h-10 w-10 border-b-2 border-black mb-3"></div>
                <p className="text-gray-600 text-sm">Loading workspaces...</p>
              </div>
            </div>
          ) : error ? (
            <div className="max-w-2xl mx-auto mt-12">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800 text-sm">
                {error}
              </div>
              <button
                onClick={fetchWorkspaces}
                className="mt-4 px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors text-sm"
              >
                Retry
              </button>
            </div>
          ) : workspaces.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-96 text-center">
              <FolderOpen size={64} className="text-gray-300 mb-4" strokeWidth={1} />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">No workspaces yet</h2>
              <p className="text-gray-500 text-sm mb-6 max-w-md">
                Create your first visualization workspace to get started
              </p>
              <button
                onClick={() => router.push('/app')}
                className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors font-medium"
              >
                Create Workspace
              </button>
            </div>
          ) : (
            <div className="max-w-5xl mx-auto">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {workspaces.map((workspace) => (
                  <div
                    key={workspace.id}
                    className="bg-white border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow cursor-pointer group"
                    onClick={() => handleLoadWorkspace(workspace.id)}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <FolderOpen size={20} className="text-gray-600" strokeWidth={1.5} />
                        <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors truncate">
                          {workspace.name}
                        </h3>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-xs text-gray-500 mb-4">
                      <Clock size={14} strokeWidth={1.5} />
                      <span>{formatDate(workspace.updated_at)}</span>
                    </div>

                    <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleLoadWorkspace(workspace.id);
                        }}
                        className="flex items-center gap-2 text-sm text-gray-700 hover:text-black transition-colors"
                      >
                        <Eye size={16} strokeWidth={1.5} />
                        Open
                      </button>
                      <span className="text-xs text-gray-400">
                        ID: {workspace.id}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
