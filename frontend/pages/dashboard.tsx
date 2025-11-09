import React from 'react';
import { useRouter } from 'next/router';
import UserDashboard from '../components/UserDashboard';

export default function DashboardPage() {
  const router = useRouter();

  React.useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth');
    }
  }, [router]);

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      {/* Simple Header */}
      <div style={{
        background: 'white',
        borderBottom: '1px solid #e0e0e0',
        padding: '16px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <h1 style={{ margin: 0, fontSize: '20px', fontWeight: 600 }}>
          Nawwa
        </h1>
        <div style={{ display: 'flex', gap: '16px' }}>
          <button
            onClick={() => router.push('/app')}
            style={{
              padding: '8px 16px',
              background: 'transparent',
              color: '#0066cc',
              border: '1px solid #0066cc',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Workspace
          </button>
          <button
            onClick={() => router.push('/profile')}
            style={{
              padding: '8px 16px',
              background: 'transparent',
              color: '#0066cc',
              border: '1px solid #ccc',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Profile
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
              border: '1px solid #ccc',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Logout
          </button>
        </div>
      </div>

      {/* Dashboard Content */}
      <UserDashboard />
    </div>
  );
}
