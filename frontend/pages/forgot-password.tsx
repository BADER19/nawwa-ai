import React, { useState } from 'react';
import { useRouter } from 'next/router';

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email) {
      setError('Please enter your email address');
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address');
      return;
    }

    setLoading(true);
    setError(null);

    // Simulate API call
    setTimeout(() => {
      setLoading(false);
      setMessage('Password reset coming soon! This feature will be available in the next release. For now, please contact support at support@nawwa.ai to reset your password.');
      setEmail('');
    }, 1000);

    // TODO: Implement backend password reset
    // try {
    //   await api.post('/auth/forgot-password', { email });
    //   setMessage('Password reset link sent! Check your email.');
    //   setEmail('');
    // } catch (err: any) {
    //   setError(err.response?.data?.detail || 'Failed to send reset link');
    // } finally {
    //   setLoading(false);
    // }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f9fafb', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
      <div style={{ maxWidth: '450px', width: '100%' }}>
        {/* Logo/Title */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h1
            onClick={() => router.push('/')}
            style={{ fontSize: '32px', fontWeight: 700, cursor: 'pointer', marginBottom: '8px' }}
          >
            Nawwa
          </h1>
          <p style={{ color: '#6b7280', fontSize: '16px' }}>
            Reset your password
          </p>
        </div>

        {/* Card */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '40px',
          border: '1px solid #e5e7eb',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)',
        }}>
          {message ? (
            <>
              {/* Success State */}
              <div style={{
                padding: '16px',
                background: '#d4edda',
                border: '1px solid #c3e6cb',
                borderRadius: '8px',
                color: '#155724',
                marginBottom: '24px',
                lineHeight: '1.6',
              }}>
                {message}
              </div>
              <button
                onClick={() => router.push('/auth')}
                style={{
                  width: '100%',
                  padding: '12px',
                  background: '#0066cc',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '16px',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                Back to Login
              </button>
            </>
          ) : (
            <>
              {/* Form */}
              <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '24px', lineHeight: '1.6' }}>
                Enter your email address and we'll send you a link to reset your password.
              </p>

              {error && (
                <div style={{
                  padding: '12px',
                  background: '#f8d7da',
                  border: '1px solid #f5c6cb',
                  borderRadius: '6px',
                  color: '#721c24',
                  marginBottom: '16px',
                  fontSize: '14px',
                }}>
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      setError(null);
                    }}
                    placeholder="you@example.com"
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '14px',
                    }}
                    disabled={loading}
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '12px',
                    background: '#0066cc',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '16px',
                    fontWeight: 600,
                    cursor: loading ? 'not-allowed' : 'pointer',
                    opacity: loading ? 0.7 : 1,
                    marginBottom: '16px',
                  }}
                >
                  {loading ? 'Sending...' : 'Send Reset Link'}
                </button>

                <button
                  type="button"
                  onClick={() => router.push('/auth')}
                  style={{
                    width: '100%',
                    padding: '12px',
                    background: 'transparent',
                    color: '#0066cc',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '14px',
                    cursor: 'pointer',
                  }}
                >
                  Back to Login
                </button>
              </form>
            </>
          )}
        </div>

        {/* Help Text */}
        <div style={{ textAlign: 'center', marginTop: '24px', fontSize: '14px', color: '#6b7280' }}>
          Remember your password?{' '}
          <span
            onClick={() => router.push('/auth')}
            style={{ color: '#0066cc', cursor: 'pointer', fontWeight: 500 }}
          >
            Sign in
          </span>
        </div>
      </div>
    </div>
  );
}
