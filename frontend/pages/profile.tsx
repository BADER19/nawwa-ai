import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { api } from '../lib/api';

interface UserProfile {
  id: number;
  email: string;
  username: string;
  created_at: string;
}

export default function ProfilePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth');
      return;
    }

    fetchProfile();
  }, [router]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const response = await api.get('/auth/me');
      setProfile(response.data);
      setFormData({
        ...formData,
        username: response.data.username || response.data.email.split('@')[0],
      });
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch profile:', err);
      setError('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    // Validate
    if (formData.newPassword && formData.newPassword !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.newPassword && !formData.currentPassword) {
      setError('Please enter your current password to change password');
      return;
    }

    // For now, just show a message since the backend doesn't have profile update endpoint
    setMessage('Profile update coming soon! This feature will be available in the next release.');
    setEditing(false);
    setTimeout(() => setMessage(null), 3000);
  };

  const formatDate = (isoDate: string) => {
    return new Date(isoDate).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: '#f9fafb' }}>
        <Header router={router} />
        <div style={{ padding: '40px', textAlign: 'center' }}>
          <div style={{ fontSize: '18px', color: '#666' }}>Loading profile...</div>
        </div>
      </div>
    );
  }

  if (error && !profile) {
    return (
      <div style={{ minHeight: '100vh', background: '#f9fafb' }}>
        <Header router={router} />
        <div style={{ padding: '40px', textAlign: 'center' }}>
          <div style={{ color: '#f44336', marginBottom: '20px' }}>{error}</div>
          <button
            onClick={fetchProfile}
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

  if (!profile) return null;

  return (
    <div style={{ minHeight: '100vh', background: '#f9fafb' }}>
      <Header router={router} />

      {/* Main Content */}
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '40px 24px' }}>
        <h1 style={{ fontSize: '32px', fontWeight: 700, marginBottom: '32px' }}>
          Account Settings
        </h1>

        {/* Success Message */}
        {message && (
          <div style={{
            padding: '12px 20px',
            background: '#d4edda',
            border: '1px solid #c3e6cb',
            borderRadius: '6px',
            color: '#155724',
            marginBottom: '20px',
          }}>
            {message}
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div style={{
            padding: '12px 20px',
            background: '#f8d7da',
            border: '1px solid #f5c6cb',
            borderRadius: '6px',
            color: '#721c24',
            marginBottom: '20px',
          }}>
            {error}
          </div>
        )}

        {/* Profile Card */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '32px',
          border: '1px solid #e5e7eb',
          marginBottom: '24px',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: 600, margin: 0 }}>
              Profile Information
            </h2>
            {!editing && (
              <button
                onClick={() => setEditing(true)}
                style={{
                  padding: '8px 16px',
                  background: '#0066cc',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px',
                }}
              >
                Edit Profile
              </button>
            )}
          </div>

          {!editing ? (
            <>
              {/* View Mode */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, color: '#6b7280', marginBottom: '4px' }}>
                  Username
                </label>
                <div style={{ fontSize: '16px', color: '#111827' }}>
                  {profile.username}
                </div>
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, color: '#6b7280', marginBottom: '4px' }}>
                  Email
                </label>
                <div style={{ fontSize: '16px', color: '#111827' }}>
                  {profile.email}
                </div>
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, color: '#6b7280', marginBottom: '4px' }}>
                  Member Since
                </label>
                <div style={{ fontSize: '16px', color: '#111827' }}>
                  {formatDate(profile.created_at)}
                </div>
              </div>
            </>
          ) : (
            <>
              {/* Edit Mode */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
                  Username
                </label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    border: '1px solid #e5e7eb',
                    borderRadius: '6px',
                    fontSize: '14px',
                  }}
                />
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
                  Email
                </label>
                <input
                  type="email"
                  value={profile.email}
                  disabled
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    border: '1px solid #e5e7eb',
                    borderRadius: '6px',
                    fontSize: '14px',
                    background: '#f9fafb',
                    color: '#6b7280',
                  }}
                />
                <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                  Email cannot be changed
                </div>
              </div>

              <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '20px', marginTop: '20px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '16px' }}>
                  Change Password
                </h3>

                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
                    Current Password
                  </label>
                  <input
                    type="password"
                    value={formData.currentPassword}
                    onChange={(e) => setFormData({ ...formData, currentPassword: e.target.value })}
                    placeholder="Enter current password"
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      border: '1px solid #e5e7eb',
                      borderRadius: '6px',
                      fontSize: '14px',
                    }}
                  />
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
                    New Password
                  </label>
                  <input
                    type="password"
                    value={formData.newPassword}
                    onChange={(e) => setFormData({ ...formData, newPassword: e.target.value })}
                    placeholder="Enter new password"
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      border: '1px solid #e5e7eb',
                      borderRadius: '6px',
                      fontSize: '14px',
                    }}
                  />
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
                    Confirm New Password
                  </label>
                  <input
                    type="password"
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                    placeholder="Confirm new password"
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      border: '1px solid #e5e7eb',
                      borderRadius: '6px',
                      fontSize: '14px',
                    }}
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '24px' }}>
                <button
                  onClick={() => {
                    setEditing(false);
                    setFormData({
                      ...formData,
                      currentPassword: '',
                      newPassword: '',
                      confirmPassword: '',
                    });
                    setError(null);
                  }}
                  style={{
                    padding: '10px 20px',
                    background: 'transparent',
                    color: '#666',
                    border: '1px solid #e5e7eb',
                    borderRadius: '6px',
                    fontSize: '14px',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  style={{
                    padding: '10px 20px',
                    background: '#0066cc',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '14px',
                    cursor: 'pointer',
                  }}
                >
                  Save Changes
                </button>
              </div>
            </>
          )}
        </div>

        {/* Danger Zone */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '32px',
          border: '1px solid #fecaca',
        }}>
          <h2 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '12px', color: '#dc2626' }}>
            Danger Zone
          </h2>
          <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '16px' }}>
            Once you delete your account, there is no going back. Please be certain.
          </p>
          <button
            onClick={() => {
              if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
                alert('Account deletion coming soon! This feature will be available in the next release.');
              }
            }}
            style={{
              padding: '10px 20px',
              background: '#dc2626',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '14px',
              cursor: 'pointer',
            }}
          >
            Delete Account
          </button>
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
    }}>
      <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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
