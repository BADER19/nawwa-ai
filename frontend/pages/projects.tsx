import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import api from '../lib/api';

interface Project {
  id: number;
  name: string;
  description: string | null;
  user_role: string;
  audience: string;
  goal: string;
  setting: string;
  tone: string;
  depth: string;
  topics: string[];
  created_at: string;
  updated_at: string;
}

export default function ProjectsPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth');
      return;
    }

    fetchProjects();
  }, [router]);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const response = await api.get('/project');
      setProjects(response.data);
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch projects:', err);
      setError(err.response?.data?.detail || 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const deleteProject = async (projectId: number) => {
    if (!confirm('Delete this project? This cannot be undone.')) return;

    try {
      await api.delete(`/project/${projectId}`);
      setProjects(projects.filter((p) => p.id !== projectId));
    } catch (err: any) {
      alert('Failed to delete project: ' + (err.response?.data?.detail || 'Unknown error'));
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  const getRoleIcon = (role: string) => {
    switch (role.toLowerCase()) {
      case 'teacher': return '👨‍🏫';
      case 'business': return '💼';
      case 'student': return '🎓';
      case 'researcher': return '🔬';
      default: return '📊';
    }
  };

  const getRoleColor = (role: string) => {
    switch (role.toLowerCase()) {
      case 'teacher': return '#4caf50';
      case 'business': return '#0066cc';
      case 'student': return '#ff9800';
      case 'researcher': return '#9c27b0';
      default: return '#666';
    }
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: '#f9fafb' }}>
        <Header router={router} />
        <div style={{ padding: '40px', textAlign: 'center' }}>
          <div style={{ fontSize: '18px', color: '#666' }}>Loading projects...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ minHeight: '100vh', background: '#f9fafb' }}>
        <Header router={router} />
        <div style={{ padding: '40px', textAlign: 'center' }}>
          <div style={{ color: '#f44336', marginBottom: '20px' }}>{error}</div>
          <button
            onClick={fetchProjects}
            style={{
              padding: '10px 20px',
              background: '#0066cc',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f9fafb' }}>
      <Header router={router} />

      {/* Main Content */}
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 24px' }}>
        {/* Page Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '32px', fontWeight: 700, marginBottom: '8px' }}>
              My Projects
            </h1>
            <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>
              Organize your visualizations into context-aware presentations
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            style={{
              padding: '12px 24px',
              background: '#0066cc',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <span style={{ fontSize: '20px' }}>+</span>
            Create Project
          </button>
        </div>

        {/* Projects Grid */}
        {projects.length === 0 ? (
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '60px 24px',
            textAlign: 'center',
            border: '1px solid #e5e7eb',
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>📁</div>
            <h3 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '8px' }}>
              No projects yet
            </h3>
            <p style={{ color: '#666', marginBottom: '24px' }}>
              Create your first project to organize your visualizations
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              style={{
                padding: '12px 24px',
                background: '#0066cc',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Create Project
            </button>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
            gap: '24px',
          }}>
            {projects.map((project) => (
              <div
                key={project.id}
                style={{
                  background: 'white',
                  borderRadius: '12px',
                  padding: '24px',
                  border: '1px solid #e5e7eb',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  position: 'relative',
                }}
                onClick={() => router.push(`/projects/${project.id}`)}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-4px)';
                  e.currentTarget.style.boxShadow = '0 12px 24px rgba(0,0,0,0.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                {/* Role Badge */}
                <div style={{
                  position: 'absolute',
                  top: '16px',
                  right: '16px',
                  fontSize: '24px',
                }}>
                  {getRoleIcon(project.user_role)}
                </div>

                {/* Project Name */}
                <h3 style={{
                  fontSize: '20px',
                  fontWeight: 600,
                  marginBottom: '8px',
                  marginRight: '40px',
                  color: '#111827',
                }}>
                  {project.name}
                </h3>

                {/* Description */}
                {project.description && (
                  <p style={{
                    fontSize: '14px',
                    color: '#6b7280',
                    marginBottom: '16px',
                    lineHeight: '1.5',
                    maxHeight: '60px',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}>
                    {project.description}
                  </p>
                )}

                {/* Context Tags */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '16px' }}>
                  <span style={{
                    padding: '4px 10px',
                    background: getRoleColor(project.user_role) + '20',
                    color: getRoleColor(project.user_role),
                    borderRadius: '12px',
                    fontSize: '11px',
                    fontWeight: 600,
                    textTransform: 'capitalize',
                  }}>
                    {project.user_role}
                  </span>
                  <span style={{
                    padding: '4px 10px',
                    background: '#f3f4f6',
                    color: '#6b7280',
                    borderRadius: '12px',
                    fontSize: '11px',
                    fontWeight: 500,
                    textTransform: 'capitalize',
                  }}>
                    {project.audience}
                  </span>
                  <span style={{
                    padding: '4px 10px',
                    background: '#f3f4f6',
                    color: '#6b7280',
                    borderRadius: '12px',
                    fontSize: '11px',
                    fontWeight: 500,
                    textTransform: 'capitalize',
                  }}>
                    {project.goal}
                  </span>
                </div>

                {/* Topics */}
                {project.topics.length > 0 && (
                  <div style={{ marginBottom: '16px' }}>
                    <div style={{ fontSize: '11px', color: '#9ca3af', marginBottom: '6px', fontWeight: 600 }}>
                      TOPICS
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                      {project.topics.slice(0, 3).map((topic, idx) => (
                        <span key={idx} style={{
                          padding: '3px 8px',
                          background: '#e0f2fe',
                          color: '#0369a1',
                          borderRadius: '8px',
                          fontSize: '10px',
                          fontWeight: 500,
                        }}>
                          {topic}
                        </span>
                      ))}
                      {project.topics.length > 3 && (
                        <span style={{
                          padding: '3px 8px',
                          color: '#6b7280',
                          fontSize: '10px',
                          fontWeight: 500,
                        }}>
                          +{project.topics.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Footer */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  paddingTop: '16px',
                  borderTop: '1px solid #e5e7eb',
                }}>
                  <span style={{ fontSize: '12px', color: '#9ca3af' }}>
                    Updated {formatDate(project.updated_at)}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteProject(project.id);
                    }}
                    style={{
                      padding: '6px 12px',
                      background: 'transparent',
                      color: '#ef4444',
                      border: '1px solid #fecaca',
                      borderRadius: '6px',
                      fontSize: '12px',
                      cursor: 'pointer',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = '#fef2f2';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'transparent';
                    }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Project Modal */}
      {showCreateModal && (
        <ProjectModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false);
            fetchProjects();
          }}
        />
      )}
    </div>
  );
}

function Header({ router }: { router: any }) {
  return (
    <div style={{
      background: 'white',
      borderBottom: '1px solid #e5e7eb',
      padding: '16px 24px',
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1
          onClick={() => router.push('/')}
          style={{ margin: 0, fontSize: '20px', fontWeight: 600, cursor: 'pointer' }}
        >
          Nawwa
        </h1>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={() => router.push('/app')}
            style={{
              padding: '8px 16px',
              background: 'transparent',
              color: '#0066cc',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Workspace
          </button>
          <button
            onClick={() => router.push('/dashboard')}
            style={{
              padding: '8px 16px',
              background: 'transparent',
              color: '#0066cc',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Dashboard
          </button>
          <button
            onClick={() => {
              localStorage.removeItem('token');
              router.push('/auth');
            }}
            style={{
              padding: '8px 16px',
              background: 'transparent',
              color: '#666',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}

interface ProjectModalProps {
  onClose: () => void;
  onSuccess: () => void;
  project?: Project;
}

function ProjectModal({ onClose, onSuccess, project }: ProjectModalProps) {
  const [formData, setFormData] = useState({
    name: project?.name || '',
    description: project?.description || '',
    user_role: project?.user_role || 'business',
    audience: project?.audience || 'general_public',
    goal: project?.goal || 'present',
    setting: project?.setting || 'boardroom',
    tone: project?.tone || 'professional',
    depth: project?.depth || 'intermediate',
    topics: project?.topics || [],
  });
  const [topicInput, setTopicInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      setError('Project name is required');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      if (project) {
        await api.put(`/project/${project.id}`, formData);
      } else {
        await api.post('/project', formData);
      }

      onSuccess();
    } catch (err: any) {
      console.error('Failed to save project:', err);
      setError(err.response?.data?.detail || 'Failed to save project');
    } finally {
      setLoading(false);
    }
  };

  const addTopic = () => {
    if (topicInput.trim() && !formData.topics.includes(topicInput.trim())) {
      setFormData({
        ...formData,
        topics: [...formData.topics, topicInput.trim()],
      });
      setTopicInput('');
    }
  };

  const removeTopic = (topic: string) => {
    setFormData({
      ...formData,
      topics: formData.topics.filter((t) => t !== topic),
    });
  };

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: '20px',
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: 'white',
          borderRadius: '16px',
          padding: '32px',
          maxWidth: '600px',
          width: '100%',
          maxHeight: '90vh',
          overflowY: 'auto',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        }}
      >
        <h2 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '24px' }}>
          {project ? 'Edit Project' : 'Create New Project'}
        </h2>

        {error && (
          <div style={{
            padding: '12px',
            background: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '6px',
            color: '#b91c1c',
            marginBottom: '16px',
            fontSize: '14px',
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Name */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
              Project Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., Q4 Sales Presentation"
              style={{
                width: '100%',
                padding: '10px 12px',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                fontSize: '14px',
              }}
            />
          </div>

          {/* Description */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Briefly describe this project..."
              rows={3}
              style={{
                width: '100%',
                padding: '10px 12px',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                fontSize: '14px',
                resize: 'vertical',
              }}
            />
          </div>

          {/* Role, Audience, Goal (Row) */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', marginBottom: '20px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
                Your Role
              </label>
              <select
                value={formData.user_role}
                onChange={(e) => setFormData({ ...formData, user_role: e.target.value })}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '6px',
                  fontSize: '14px',
                }}
              >
                <option value="teacher">Teacher</option>
                <option value="business">Business</option>
                <option value="student">Student</option>
                <option value="researcher">Researcher</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
                Audience
              </label>
              <select
                value={formData.audience}
                onChange={(e) => setFormData({ ...formData, audience: e.target.value })}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '6px',
                  fontSize: '14px',
                }}
              >
                <option value="students">Students</option>
                <option value="executives">Executives</option>
                <option value="peers">Peers</option>
                <option value="self">Self</option>
                <option value="general_public">General Public</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
                Goal
              </label>
              <select
                value={formData.goal}
                onChange={(e) => setFormData({ ...formData, goal: e.target.value })}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '6px',
                  fontSize: '14px',
                }}
              >
                <option value="teach">Teach</option>
                <option value="present">Present</option>
                <option value="learn">Learn</option>
                <option value="analyze">Analyze</option>
                <option value="explain">Explain</option>
              </select>
            </div>
          </div>

          {/* Setting, Tone, Depth (Row) */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', marginBottom: '20px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
                Setting
              </label>
              <select
                value={formData.setting}
                onChange={(e) => setFormData({ ...formData, setting: e.target.value })}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '6px',
                  fontSize: '14px',
                }}
              >
                <option value="classroom">Classroom</option>
                <option value="boardroom">Boardroom</option>
                <option value="study">Study</option>
                <option value="paper">Paper</option>
                <option value="blog">Blog</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
                Tone
              </label>
              <select
                value={formData.tone}
                onChange={(e) => setFormData({ ...formData, tone: e.target.value })}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '6px',
                  fontSize: '14px',
                }}
              >
                <option value="simple">Simple</option>
                <option value="professional">Professional</option>
                <option value="academic">Academic</option>
                <option value="casual">Casual</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
                Depth
              </label>
              <select
                value={formData.depth}
                onChange={(e) => setFormData({ ...formData, depth: e.target.value })}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '6px',
                  fontSize: '14px',
                }}
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="expert">Expert</option>
              </select>
            </div>
          </div>

          {/* Topics */}
          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
              Topics
            </label>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
              <input
                type="text"
                value={topicInput}
                onChange={(e) => setTopicInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addTopic();
                  }
                }}
                placeholder="Add a topic..."
                style={{
                  flex: 1,
                  padding: '8px 12px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '6px',
                  fontSize: '14px',
                }}
              />
              <button
                type="button"
                onClick={addTopic}
                style={{
                  padding: '8px 16px',
                  background: '#0066cc',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '14px',
                  cursor: 'pointer',
                }}
              >
                Add
              </button>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {formData.topics.map((topic) => (
                <span
                  key={topic}
                  style={{
                    padding: '6px 12px',
                    background: '#e0f2fe',
                    color: '#0369a1',
                    borderRadius: '12px',
                    fontSize: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}
                >
                  {topic}
                  <button
                    type="button"
                    onClick={() => removeTopic(topic)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#0369a1',
                      cursor: 'pointer',
                      fontSize: '14px',
                      padding: 0,
                      lineHeight: 1,
                    }}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              style={{
                padding: '10px 20px',
                background: 'transparent',
                color: '#666',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                fontSize: '14px',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.5 : 1,
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              style={{
                padding: '10px 20px',
                background: '#0066cc',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.7 : 1,
              }}
            >
              {loading ? 'Saving...' : (project ? 'Save Changes' : 'Create Project')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
