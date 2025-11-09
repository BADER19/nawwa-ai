import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { User, CreditCard, FolderOpen, Lock, Info, Check, XCircle, AlertTriangle } from 'lucide-react';
import { api } from '../lib/api';

type SettingsTab = 'general' | 'subscription' | 'projects' | 'data';

interface UserProfile {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

interface SubscriptionInfo {
  tier: string;
  status: string;
  usage_count: number;
  usage_limit: number | string;
  usage_percentage: number;
  usage_reset_date: string;
  features: string[];
  has_stripe_subscription: boolean;
}

interface Project {
  id: number;
  name: string;
  description: string | null;
  user_role: string;
  audience: string;
  goal: string;
  created_at: string;
  updated_at: string;
}

export default function SettingsPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<SettingsTab>('general');
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [subscription, setSubscription] = useState<SubscriptionInfo | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth');
      return;
    }

    // Get active tab from URL query
    const tab = router.query.tab as SettingsTab;
    if (tab && ['general', 'subscription', 'projects', 'data'].includes(tab)) {
      setActiveTab(tab);
    }

    fetchData();
  }, [router]);

  const fetchData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchProfile(),
        fetchSubscription(),
        fetchProjects(),
      ]);
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchProfile = async () => {
    try {
      console.log('[Settings] Fetching profile from /auth/me');
      const response = await api.get('/auth/me');
      console.log('[Settings] Profile response:', response.data);
      setProfile(response.data);
    } catch (err) {
      console.error('[Settings] Failed to fetch profile:', err);
    }
  };

  const fetchSubscription = async () => {
    try {
      const response = await api.get('/subscription/subscription-info');
      setSubscription(response.data);
    } catch (err) {
      console.error('Failed to fetch subscription:', err);
    }
  };

  const fetchProjects = async () => {
    try {
      const response = await api.get('/project');
      setProjects(response.data);
    } catch (err) {
      console.error('Failed to fetch projects:', err);
    }
  };

  const handleTabChange = (tab: SettingsTab) => {
    setActiveTab(tab);
    router.push(`/settings?tab=${tab}`, undefined, { shallow: true });
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f9fafb' }}>
      {/* Header */}
      <Header router={router} />

      <div style={{ display: 'flex', minHeight: 'calc(100vh - 64px)' }}>
        {/* Sidebar */}
        <Sidebar activeTab={activeTab} onTabChange={handleTabChange} />

        {/* Main Content */}
        <div style={{ flex: 1, padding: '40px', overflowY: 'auto' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '60px', color: '#666' }}>
              Loading...
            </div>
          ) : (
            <>
              {activeTab === 'general' && (
                <GeneralSettings profile={profile} onUpdate={fetchProfile} />
              )}
              {activeTab === 'subscription' && (
                <SubscriptionSettings subscription={subscription} router={router} />
              )}
              {activeTab === 'projects' && (
                <ProjectsSettings projects={projects} router={router} onUpdate={fetchProjects} />
              )}
              {activeTab === 'data' && (
                <DataSettings router={router} />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function Header({ router }: { router: any }) {
  return (
    <div style={{
      background: 'white',
      borderBottom: '1px solid #e5e7eb',
      padding: '16px 24px',
      height: '64px',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '100%' }}>
        <h1
          onClick={() => router.push('/')}
          style={{ margin: 0, fontSize: '20px', fontWeight: 600, cursor: 'pointer' }}
        >
          Nawwa
        </h1>
        <button
          onClick={() => router.push('/app')}
          style={{
            padding: '8px 16px',
            background: '#0066cc',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 500,
          }}
        >
          Back to Workspace
        </button>
      </div>
    </div>
  );
}

function Sidebar({ activeTab, onTabChange }: { activeTab: SettingsTab; onTabChange: (tab: SettingsTab) => void }) {
  const tabs = [
    { id: 'general', icon: <User size={20} strokeWidth={1.5} />, label: 'General', description: 'Profile & Account' },
    { id: 'subscription', icon: <CreditCard size={20} strokeWidth={1.5} />, label: 'Subscription', description: 'Usage & Billing' },
    { id: 'projects', icon: <FolderOpen size={20} strokeWidth={1.5} />, label: 'Projects', description: 'Manage Projects' },
    { id: 'data', icon: <Lock size={20} strokeWidth={1.5} />, label: 'Data & Privacy', description: 'Export & Delete' },
  ];

  return (
    <div style={{
      width: '280px',
      background: 'white',
      borderRight: '1px solid #e5e7eb',
      padding: '24px 0',
    }}>
      <div style={{ padding: '0 24px', marginBottom: '24px' }}>
        <h2 style={{ fontSize: '24px', fontWeight: 700, margin: 0 }}>Settings</h2>
      </div>

      <nav>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id as SettingsTab)}
            style={{
              width: '100%',
              padding: '12px 24px',
              background: activeTab === tab.id ? '#f3f4f6' : 'transparent',
              border: 'none',
              borderLeft: activeTab === tab.id ? '3px solid #0066cc' : '3px solid transparent',
              textAlign: 'left',
              cursor: 'pointer',
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
            }}
            onMouseEnter={(e) => {
              if (activeTab !== tab.id) {
                e.currentTarget.style.background = '#f9fafb';
              }
            }}
            onMouseLeave={(e) => {
              if (activeTab !== tab.id) {
                e.currentTarget.style.background = 'transparent';
              }
            }}
          >
            <span style={{ display: 'flex', alignItems: 'center', color: activeTab === tab.id ? '#0066cc' : '#6b7280' }}>{tab.icon}</span>
            <div>
              <div style={{
                fontSize: '14px',
                fontWeight: activeTab === tab.id ? 600 : 500,
                color: activeTab === tab.id ? '#0066cc' : '#111827',
                marginBottom: '2px',
              }}>
                {tab.label}
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>
                {tab.description}
              </div>
            </div>
          </button>
        ))}
      </nav>
    </div>
  );
}

function GeneralSettings({ profile, onUpdate }: { profile: UserProfile | null; onUpdate: () => void }) {
  const [isEditing, setIsEditing] = useState(false);
  const [initialProfile, setInitialProfile] = useState<UserProfile | null>(null);
  const [draftProfile, setDraftProfile] = useState({ username: '', email: '' });
  const [errors, setErrors] = useState({ username: '', email: '' });
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const usernameInputRef = React.useRef<HTMLInputElement>(null);
  const editButtonRef = React.useRef<HTMLButtonElement>(null);

  // Initialize profile data
  React.useEffect(() => {
    if (profile && !initialProfile) {
      setInitialProfile(profile);
      setDraftProfile({ username: profile.username, email: profile.email });
    }
  }, [profile, initialProfile]);

  // Validation functions
  const validateUsername = (username: string): string => {
    if (!username || username.length < 3) return 'Username must be at least 3 characters';
    if (username.length > 30) return 'Username must be less than 30 characters';
    if (!/^[a-zA-Z0-9_]+$/.test(username)) return 'Username can only contain letters, numbers, and underscores';
    return '';
  };

  const validateEmail = (email: string): string => {
    if (!email) return 'Email is required';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return 'Please enter a valid email address';
    return '';
  };

  // Check if form is dirty
  const isDirty = initialProfile && (
    draftProfile.username !== initialProfile.username ||
    draftProfile.email !== initialProfile.email
  );

  // Check if form is valid
  const isValid = !errors.username && !errors.email && isDirty;

  const handleEnterEdit = () => {
    setIsEditing(true);
    setMessage(null);
    setTimeout(() => usernameInputRef.current?.focus(), 100);
  };

  const handleCancel = () => {
    if (isDirty) {
      if (!window.confirm('Discard unsaved changes?')) return;
    }
    setIsEditing(false);
    if (initialProfile) {
      setDraftProfile({ username: initialProfile.username, email: initialProfile.email });
    }
    setErrors({ username: '', email: '' });
    setMessage(null);
    setTimeout(() => editButtonRef.current?.focus(), 100);
  };

  const handleSave = async () => {
    // Final validation
    const usernameError = validateUsername(draftProfile.username);
    const emailError = validateEmail(draftProfile.email);

    if (usernameError || emailError) {
      setErrors({ username: usernameError, email: emailError });
      return;
    }

    setIsSaving(true);
    try {
      await api.patch('/auth/me', {
        username: draftProfile.username,
        email: draftProfile.email,
      });

      setMessage({ type: 'success', text: 'Profile updated successfully!' });
      setInitialProfile({ ...initialProfile!, username: draftProfile.username, email: draftProfile.email });
      setIsEditing(false);
      onUpdate();
      setTimeout(() => {
        setMessage(null);
        editButtonRef.current?.focus();
      }, 3000);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to update profile';
      setMessage({ type: 'error', text: errorMsg });
    } finally {
      setIsSaving(false);
    }
  };

  const handleInputChange = (field: 'username' | 'email', value: string) => {
    setDraftProfile({ ...draftProfile, [field]: value });
    // Clear error for this field when user starts typing
    if (errors[field]) {
      setErrors({ ...errors, [field]: '' });
    }
  };

  const handleInputBlur = (field: 'username' | 'email') => {
    const value = draftProfile[field];
    const error = field === 'username' ? validateUsername(value) : validateEmail(value);
    setErrors({ ...errors, [field]: error });
  };

  if (!profile) return <div>Loading profile...</div>;

  return (
    <div style={{ maxWidth: '960px' }}>
      <h1 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '8px', color: '#111827' }}>Account Settings</h1>
      <p style={{ color: '#6b7280', marginBottom: '32px', fontSize: '14px' }}>
        Manage your account information and preferences
      </p>

      {message && (
        <div style={{
          padding: '12px 20px',
          background: message.type === 'success' ? '#d1fae5' : '#fee2e2',
          border: `1px solid ${message.type === 'success' ? '#a7f3d0' : '#fecaca'}`,
          borderRadius: '8px',
          color: message.type === 'success' ? '#065f46' : '#991b1b',
          marginBottom: '24px',
          fontSize: '14px',
        }}>
          {message.text}
        </div>
      )}

      {/* Profile Information Card */}
      <section
        aria-labelledby="profile-heading"
        style={{
          background: 'white',
          border: '1px solid #e5e7eb',
          borderRadius: '12px',
          padding: '24px',
          marginBottom: '32px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
          transition: 'all 0.2s ease',
          overflow: 'hidden'
        }}
      >
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px'
        }}>
          <h3 id="profile-heading" style={{ fontSize: '18px', fontWeight: 600, color: '#111827', margin: 0 }}>
            Profile Information
          </h3>
          {!isEditing && (
            <button
              ref={editButtonRef}
              onClick={handleEnterEdit}
              style={{
                padding: '10px 20px',
                background: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 600,
                transition: 'all 0.2s',
                boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#2563eb';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#3b82f6';
              }}
            >
              Edit Profile
            </button>
          )}
        </div>

        {!isEditing ? (
          // View State
          <>
            <Field label="Username" value={profile.username} />
            <Field label="Email" value={profile.email} />
            <Field
              label="Member Since"
              value={new Date(profile.created_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            />
          </>
        ) : (
          // Edit State
          <div style={{ animation: 'fadeIn 0.2s ease' }}>
            <InputFieldWithError
              ref={usernameInputRef}
              label="Username"
              value={draftProfile.username}
              onChange={(v) => handleInputChange('username', v)}
              onBlur={() => handleInputBlur('username')}
              error={errors.username}
              placeholder="Enter username"
              ariaInvalid={!!errors.username}
            />
            <InputFieldWithError
              label="Email"
              value={draftProfile.email}
              onChange={(v) => handleInputChange('email', v)}
              onBlur={() => handleInputBlur('email')}
              error={errors.email}
              placeholder="Enter email"
              ariaInvalid={!!errors.email}
            />
            <Field
              label="Member Since"
              value={new Date(profile.created_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            />

            <div style={{
              display: 'flex',
              gap: '12px',
              marginTop: '24px',
              justifyContent: 'flex-end',
              flexWrap: 'wrap'
            }}>
              <button
                onClick={handleCancel}
                style={{
                  padding: '10px 20px',
                  background: 'transparent',
                  color: '#6b7280',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: 500,
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = '#f9fafb'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={!isValid || isSaving}
                style={{
                  padding: '10px 20px',
                  background: (!isValid || isSaving) ? '#d1d5db' : '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: (!isValid || isSaving) ? 'not-allowed' : 'pointer',
                  fontSize: '14px',
                  fontWeight: 600,
                  transition: 'all 0.2s',
                  opacity: (!isValid || isSaving) ? 0.6 : 1
                }}
                onMouseEnter={(e) => {
                  if (isValid && !isSaving) {
                    e.currentTarget.style.background = '#2563eb';
                  }
                }}
                onMouseLeave={(e) => {
                  if (isValid && !isSaving) {
                    e.currentTarget.style.background = '#3b82f6';
                  }
                }}
              >
                {isSaving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        )}
      </section>

      {/* Danger Zone */}
      <section
        aria-labelledby="danger-zone-heading"
        style={{
          background: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '12px',
          padding: '24px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
        }}
      >
        <h3 id="danger-zone-heading" style={{
          fontSize: '18px',
          fontWeight: 700,
          color: '#dc2626',
          marginBottom: '12px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <AlertTriangle size={20} strokeWidth={2} style={{ flexShrink: 0 }} />
          Danger Zone
        </h3>
        <p style={{
          fontSize: '14px',
          color: '#991b1b',
          marginBottom: '20px',
          lineHeight: '1.6'
        }}>
          Once you delete your account, there is no going back. This action cannot be undone. All your data, workspaces, and visualizations will be permanently deleted.
        </p>
        <button
          onClick={() => {
            if (window.confirm('Are you absolutely sure? This action cannot be undone. All your data, projects, and visualizations will be permanently deleted.')) {
              alert('Account deletion coming soon! Please contact support@nawwa.ai to delete your account.');
            }
          }}
          style={{
            padding: '10px 20px',
            background: '#dc2626',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 600,
            transition: 'all 0.2s',
            boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = '#b91c1c';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = '#dc2626';
          }}
        >
          <AlertTriangle size={16} strokeWidth={2} />
          Delete Account
        </button>
      </section>
    </div>
  );
}

function SubscriptionSettings({ subscription, router }: { subscription: SubscriptionInfo | null; router: any }) {
  if (!subscription) return <div>Loading subscription...</div>;

  const getTierColor = (tier: string) => {
    switch (tier.toUpperCase()) {
      case 'FREE': return '#999';
      case 'PRO': return '#0066cc';
      case 'TEAM': return '#6c2c91';
      case 'ENTERPRISE': return '#d83b01';
      default: return '#666';
    }
  };

  const getUsageColor = (percentage: number) => {
    if (percentage < 50) return '#4caf50';
    if (percentage < 80) return '#ff9800';
    return '#f44336';
  };

  const usageLimit = typeof subscription.usage_limit === 'number' ? subscription.usage_limit : 'Unlimited';
  const usagePercentage = subscription.usage_percentage || 0;

  return (
    <div style={{ maxWidth: '800px' }}>
      <h1 style={{ fontSize: '32px', fontWeight: 700, marginBottom: '8px' }}>Subscription & Usage</h1>
      <p style={{ color: '#6b7280', marginBottom: '32px' }}>
        Manage your subscription plan and monitor your usage
      </p>

      {/* Current Plan */}
      <Section title="Current Plan">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <div>
            <div style={{
              fontSize: '28px',
              fontWeight: 700,
              color: getTierColor(subscription.tier),
              textTransform: 'uppercase',
              marginBottom: '4px',
            }}>
              {subscription.tier}
            </div>
            <div style={{
              display: 'inline-block',
              padding: '4px 12px',
              background: subscription.status === 'active' ? '#d4edda' : '#fff3cd',
              color: subscription.status === 'active' ? '#155724' : '#856404',
              borderRadius: '12px',
              fontSize: '12px',
              fontWeight: 600,
              textTransform: 'uppercase',
            }}>
              {subscription.status}
            </div>
          </div>
          {subscription.tier !== 'ENTERPRISE' && (
            <button
              onClick={() => router.push('/pricing')}
              style={{
                padding: '10px 20px',
                background: '#0066cc',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 500,
              }}
            >
              Upgrade Plan
            </button>
          )}
        </div>

        {/* Features */}
        <div>
          <div style={{ fontSize: '14px', fontWeight: 600, marginBottom: '12px', color: '#6b7280' }}>
            INCLUDED FEATURES
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {subscription.features.map((feature, idx) => (
              <span
                key={idx}
                style={{
                  padding: '6px 12px',
                  background: '#f3f4f6',
                  borderRadius: '16px',
                  fontSize: '12px',
                  color: '#374151',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                <Check size={14} strokeWidth={2} style={{ color: '#10b981' }} />
                {feature.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        </div>
      </Section>

      {/* Usage */}
      <Section title="Usage This Month">
        <div style={{ marginBottom: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '14px', fontWeight: 600 }}>Visualizations</span>
            <span style={{ fontSize: '14px', color: '#6b7280' }}>
              Resets {new Date(subscription.usage_reset_date).toLocaleDateString()}
            </span>
          </div>

          {/* Progress Bar */}
          <div style={{
            width: '100%',
            height: '12px',
            background: '#e5e7eb',
            borderRadius: '6px',
            overflow: 'hidden',
            marginBottom: '8px',
          }}>
            <div style={{
              width: `${Math.min(usagePercentage, 100)}%`,
              height: '100%',
              background: getUsageColor(usagePercentage),
              transition: 'width 0.3s ease',
            }} />
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
            <span style={{ color: '#6b7280' }}>
              {subscription.usage_count.toLocaleString()} used
            </span>
            <span style={{ fontWeight: 600 }}>
              {usageLimit === 'Unlimited' ? 'Unlimited' : `${usageLimit.toLocaleString()} limit`}
            </span>
          </div>
        </div>

        {usagePercentage >= 80 && (
          <div style={{
            padding: '12px',
            background: usagePercentage >= 100 ? '#fef2f2' : '#fffbeb',
            border: `1px solid ${usagePercentage >= 100 ? '#fecaca' : '#fef3c7'}`,
            borderRadius: '8px',
            fontSize: '13px',
            color: usagePercentage >= 100 ? '#991b1b' : '#92400e',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            {usagePercentage >= 100 ? (
              <>
                <XCircle size={16} strokeWidth={2} style={{ flexShrink: 0 }} />
                <span>You've reached your monthly limit. Upgrade to continue.</span>
              </>
            ) : (
              <>
                <AlertTriangle size={16} strokeWidth={2} style={{ flexShrink: 0 }} />
                <span>You've used {usagePercentage.toFixed(0)}% of your monthly limit</span>
              </>
            )}
          </div>
        )}
      </Section>

      {/* Billing */}
      {subscription.has_stripe_subscription && (
        <Section title="Billing">
          <button
            onClick={async () => {
              try {
                const response = await api.post('/subscription/create-portal-session', {
                  return_url: window.location.origin + '/settings?tab=subscription'
                });
                window.location.href = response.data.url;
              } catch (err) {
                alert('Failed to open billing portal');
              }
            }}
            style={{
              padding: '10px 20px',
              background: 'transparent',
              color: '#0066cc',
              border: '1px solid #0066cc',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Manage Billing
          </button>
        </Section>
      )}
    </div>
  );
}

function ProjectsSettings({ projects, router, onUpdate }: { projects: Project[]; router: any; onUpdate: () => void }) {
  return (
    <div style={{ maxWidth: '800px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <div>
          <h1 style={{ fontSize: '32px', fontWeight: 700, marginBottom: '8px' }}>Projects</h1>
          <p style={{ color: '#6b7280', margin: 0 }}>
            Manage your visualization projects
          </p>
        </div>
        <button
          onClick={() => router.push('/projects')}
          style={{
            padding: '10px 20px',
            background: '#0066cc',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 500,
          }}
        >
          View All Projects
        </button>
      </div>

      {projects.length === 0 ? (
        <Section title="">
          <div style={{ textAlign: 'center', padding: '40px 20px' }}>
            <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'center' }}>
              <FolderOpen size={48} strokeWidth={1} style={{ color: '#d1d5db' }} />
            </div>
            <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>No projects yet</h3>
            <p style={{ color: '#6b7280', marginBottom: '24px' }}>
              Create your first project to organize your visualizations
            </p>
            <button
              onClick={() => router.push('/projects')}
              style={{
                padding: '10px 20px',
                background: '#0066cc',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 500,
              }}
            >
              Create Project
            </button>
          </div>
        </Section>
      ) : (
        <Section title={`${projects.length} Project${projects.length !== 1 ? 's' : ''}`}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {projects.slice(0, 5).map((project) => (
              <div
                key={project.id}
                onClick={() => router.push(`/projects/${project.id}`)}
                style={{
                  padding: '16px',
                  background: '#f9fafb',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = '#f3f4f6';
                  e.currentTarget.style.borderColor = '#d1d5db';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = '#f9fafb';
                  e.currentTarget.style.borderColor = '#e5e7eb';
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: '16px', fontWeight: 600, marginBottom: '4px' }}>
                      {project.name}
                    </div>
                    {project.description && (
                      <div style={{ fontSize: '14px', color: '#6b7280' }}>
                        {project.description}
                      </div>
                    )}
                  </div>
                  <span style={{ fontSize: '24px' }}>→</span>
                </div>
              </div>
            ))}
          </div>

          {projects.length > 5 && (
            <button
              onClick={() => router.push('/projects')}
              style={{
                width: '100%',
                padding: '12px',
                background: 'transparent',
                color: '#0066cc',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                marginTop: '12px',
              }}
            >
              View All {projects.length} Projects
            </button>
          )}
        </Section>
      )}
    </div>
  );
}

function DataSettings({ router }: { router: any }) {
  const [exportLoading, setExportLoading] = useState(false);

  const handleExport = async () => {
    setExportLoading(true);
    // Simulate export
    setTimeout(() => {
      alert('Export feature coming soon! This will allow you to download all your data.');
      setExportLoading(false);
    }, 1000);
  };

  const handleDeleteAccount = () => {
    if (confirm('Are you absolutely sure? This action cannot be undone. All your data, projects, and visualizations will be permanently deleted.')) {
      alert('Account deletion coming soon! Please contact support@nawwa.ai to delete your account.');
    }
  };

  return (
    <div style={{ maxWidth: '800px' }}>
      <h1 style={{ fontSize: '32px', fontWeight: 700, marginBottom: '8px' }}>Data & Privacy</h1>
      <p style={{ color: '#6b7280', marginBottom: '32px' }}>
        Manage your data and account privacy settings
      </p>

      {/* Export Data */}
      <Section title="Export Data">
        <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '16px', lineHeight: '1.6' }}>
          Download a copy of all your data including visualizations, projects, and chat history.
        </p>
        <button
          onClick={handleExport}
          disabled={exportLoading}
          style={{
            padding: '10px 20px',
            background: '#0066cc',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: exportLoading ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            fontWeight: 500,
            opacity: exportLoading ? 0.6 : 1,
          }}
        >
          {exportLoading ? 'Preparing...' : 'Export My Data'}
        </button>
      </Section>

      {/* Clear Chat History */}
      <Section title="Clear Chat History">
        <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '16px', lineHeight: '1.6' }}>
          Delete all your conversation history. This action cannot be undone.
        </p>
        <button
          onClick={async () => {
            if (confirm('Clear all chat history? This cannot be undone.')) {
              try {
                await api.delete('/chat/messages');
                alert('Chat history cleared successfully!');
              } catch (err) {
                alert('Failed to clear chat history');
              }
            }
          }}
          style={{
            padding: '10px 20px',
            background: 'transparent',
            color: '#ef4444',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
          }}
        >
          Clear Chat History
        </button>
      </Section>

      {/* Delete Account - Danger Zone */}
      <Section
        title="Delete Account"
        titleColor="#dc2626"
        style={{ border: '1px solid #fecaca', background: '#fef2f2' }}
      >
        <p style={{ fontSize: '14px', color: '#991b1b', marginBottom: '16px', lineHeight: '1.6', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertTriangle size={18} strokeWidth={2} style={{ flexShrink: 0 }} />
          <span>Warning: This action is irreversible. All your data will be permanently deleted.</span>
        </p>
        <button
          onClick={handleDeleteAccount}
          style={{
            padding: '10px 20px',
            background: '#dc2626',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 500,
          }}
        >
          Delete Account
        </button>
      </Section>
    </div>
  );
}

// Helper Components

function Section({
  title,
  children,
  titleColor = '#111827',
  style = {}
}: {
  title: string;
  children: React.ReactNode;
  titleColor?: string;
  style?: React.CSSProperties;
}) {
  return (
    <div style={{
      background: 'white',
      border: '1px solid #e5e7eb',
      borderRadius: '12px',
      padding: '24px',
      marginBottom: '24px',
      ...style,
    }}>
      {title && (
        <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '20px', color: titleColor }}>
          {title}
        </h3>
      )}
      {children}
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#6b7280', marginBottom: '6px' }}>
        {label}
      </label>
      <div style={{ fontSize: '15px', color: '#111827', fontWeight: 500 }}>
        {value}
      </div>
    </div>
  );
}

function InputField({
  label,
  value,
  onChange,
  type = 'text',
  placeholder = '',
  disabled = false,
  helper = '',
}: {
  label: string;
  value: string;
  onChange?: (value: string) => void;
  type?: string;
  placeholder?: string;
  disabled?: boolean;
  helper?: string;
}) {
  return (
    <div style={{ marginBottom: '20px' }}>
      <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
        {label}
      </label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        style={{
          width: '100%',
          padding: '10px 12px',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          fontSize: '14px',
          background: disabled ? '#f9fafb' : 'white',
          color: disabled ? '#6b7280' : '#111827',
        }}
      />
      {helper && (
        <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
          {helper}
        </div>
      )}
    </div>
  );
}

const InputFieldWithError = React.forwardRef<HTMLInputElement, {
  label: string;
  value: string;
  onChange: (value: string) => void;
  onBlur?: () => void;
  error?: string;
  placeholder?: string;
  type?: string;
  ariaInvalid?: boolean;
}>((props, ref) => {
  const { label, value, onChange, onBlur, error, placeholder = '', type = 'text', ariaInvalid = false } = props;
  const errorId = `${label.toLowerCase().replace(/\s/g, '-')}-error`;

  return (
    <div style={{ marginBottom: '20px' }}>
      <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px', color: '#111827' }}>
        {label}
      </label>
      <input
        ref={ref}
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onBlur={onBlur}
        placeholder={placeholder}
        aria-invalid={ariaInvalid}
        aria-describedby={error ? errorId : undefined}
        style={{
          width: '100%',
          padding: '10px 12px',
          border: `1px solid ${error ? '#ef4444' : '#e5e7eb'}`,
          borderRadius: '8px',
          fontSize: '14px',
          background: 'white',
          color: '#111827',
          outline: 'none',
          transition: 'border-color 0.2s'
        }}
        onFocus={(e) => {
          if (!error) e.currentTarget.style.borderColor = '#0066cc';
        }}
      />
      {error && (
        <div id={errorId} role="alert" style={{
          fontSize: '13px',
          color: '#ef4444',
          marginTop: '6px',
          display: 'flex',
          alignItems: 'center',
          gap: '4px'
        }}>
          <AlertTriangle size={14} strokeWidth={2} style={{ flexShrink: 0 }} />
          {error}
        </div>
      )}
    </div>
  );
});
