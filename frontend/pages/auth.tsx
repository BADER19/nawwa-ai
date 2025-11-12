import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { apiPost } from '../lib/api';

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const router = useRouter();

  // Clear token when switching to signup mode to prevent data leakage
  const switchToSignup = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
    }
    setIsLogin(false);
    setError('');
  };

  // Safe error setter that ensures only strings are set
  const setErrorSafe = (errorValue: any) => {
    if (typeof errorValue === 'string') {
      setError(errorValue);
    } else if (errorValue && typeof errorValue === 'object') {
      // Try to extract a meaningful message
      const msg = errorValue.msg || errorValue.message || errorValue.detail;
      setError(typeof msg === 'string' ? msg : 'An error occurred. Please try again.');
    } else {
      setError('An error occurred. Please try again.');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setErrorSafe('Please fill in all fields');
      return;
    }

    if (!isLogin && !username) {
      setErrorSafe('Please enter a username');
      return;
    }

    if (!isLogin && password !== confirmPassword) {
      setErrorSafe('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setErrorSafe('Password must be at least 8 characters');
      return;
    }

    setIsLoading(true);

    try {
      if (isLogin) {
        const data = await apiPost<{ access_token: string }>('/auth/login', { email, password });
        if (typeof window !== 'undefined') {
          localStorage.setItem('token', data.access_token);
        }
        router.push('/app');
      } else {
        // CRITICAL FIX: Clear old token before signup to prevent data leakage
        if (typeof window !== 'undefined') {
          localStorage.removeItem('token');
        }

        await apiPost('/auth/signup', { email, password, username });
        setError('');
        setIsLogin(true);
        setUsername('');
        setPassword('');
        setConfirmPassword('');
        setTimeout(() => {
          alert('Account created successfully! Please login.');
        }, 100);
      }
    } catch (err: any) {
      console.error('Signup/Login error:', err);
      console.log('Error response:', err.response?.data);

      // Handle Pydantic validation errors (422 status)
      let errorMessage: string = isLogin ? 'Invalid email or password' : 'Failed to create account';

      try {
        if (err.response?.data?.detail) {
          const detail = err.response.data.detail;

          // If detail is an array (Pydantic validation errors)
          if (Array.isArray(detail) && detail.length > 0) {
            // Extract the first error message and ensure it's a string
            const firstError = detail[0];
            if (firstError && typeof firstError === 'object' && firstError.msg) {
              // Remove "Value error, " prefix if present
              errorMessage = String(firstError.msg).replace(/^Value error,\s*/i, '');
            } else if (typeof firstError === 'string') {
              errorMessage = firstError;
            } else {
              // Fallback: try to extract any readable message
              errorMessage = JSON.stringify(firstError);
            }
          }
          // If detail is a string (simple error)
          else if (typeof detail === 'string') {
            errorMessage = detail;
          }
          // If detail is an object with msg field
          else if (typeof detail === 'object' && detail !== null && detail.msg) {
            errorMessage = String(detail.msg);
          }
        }
      } catch (parseError) {
        console.error('Error parsing error response:', parseError);
        errorMessage = 'An unexpected error occurred. Please try again.';
      }

      // Final safety check: ensure errorMessage is always a string
      if (typeof errorMessage !== 'string' || errorMessage.trim() === '') {
        errorMessage = 'An error occurred. Please try again.';
      }

      console.log('Final error message to display:', errorMessage);
      setErrorSafe(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: '#fcfcfc',
      color: '#000'
    }}>
      {/* Header - matching landing page */}
      <header style={{
        position: 'fixed',
        top: '16px',
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 20,
        display: 'flex',
        height: '60px',
        width: '100%',
        maxWidth: '80rem',
        color: '#374151',
        background: 'white',
        padding: '0 3%',
        borderRadius: '6px',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        backdropFilter: 'blur(16px)',
        opacity: 0.99,
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <a style={{
          display: 'flex',
          padding: '4px',
          gap: '8px',
          alignItems: 'center',
          textDecoration: 'none',
          color: 'inherit'
        }} href="/">
          <div style={{ height: '40px', maxWidth: '120px' }}>
            <img
              src="/assets/logo/logo.svg"
              alt="logo"
              style={{ objectFit: 'contain', height: '100%', width: '100%' }}
            />
          </div>
          <span style={{
            textTransform: 'uppercase',
            fontSize: '16px',
            fontWeight: 500
          }}>Nawwa</span>
        </a>
        <button
          onClick={() => router.push('/')}
          style={{
            fontSize: '14px',
            padding: '8px 16px',
            borderRadius: '6px',
            border: 'none',
            background: 'transparent',
            cursor: 'pointer',
            transition: 'background 0.2s'
          }}
          onMouseOver={(e) => e.currentTarget.style.background = '#f3f4f6'}
          onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
        >
          Back to Home
        </button>
      </header>

      {/* Main Content */}
      <div style={{
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '96px 16px'
      }}>
        <div style={{ width: '100%', maxWidth: '448px', position: 'relative' }}>
          {/* Purple gradient accent (subtle background) */}
          <div style={{
            position: 'absolute',
            left: '50%',
            top: '-48px',
            transform: 'translateX(-50%)',
            height: '200px',
            width: '200px',
            background: 'linear-gradient(to bottom right, #a855f7, #3b82f6)',
            borderRadius: '50%',
            filter: 'blur(120px)',
            opacity: 0.3,
            pointerEvents: 'none',
            zIndex: 0
          }} />

          {/* Auth Card */}
          <div style={{
            position: 'relative',
            zIndex: 10,
            background: 'white',
            border: '1px solid #e5e7eb',
            borderRadius: '12px',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
            padding: '32px'
          }}>
            {/* Header */}
            <div style={{ textAlign: 'center', marginBottom: '32px' }}>
              <h2 style={{ fontSize: '30px', fontWeight: 600, marginBottom: '8px' }}>
                {isLogin ? 'Welcome back' : 'Create account'}
              </h2>
              <p style={{ color: '#6b7280', fontSize: '14px' }}>
                {isLogin ? 'Sign in to continue to Nawwa' : 'Get started with Nawwa today'}
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div style={{
                marginBottom: '24px',
                padding: '12px',
                background: '#fef2f2',
                border: '1px solid #fecaca',
                borderRadius: '8px',
                color: '#dc2626',
                fontSize: '14px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                {typeof error === 'string' ? error : 'An error occurred. Please try again.'}
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {/* Email */}
              <div>
                <label style={{
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: 500,
                  marginBottom: '8px'
                }}>
                  Email address
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    background: '#f9fafb',
                    border: '1px solid #d1d5db',
                    borderRadius: '8px',
                    fontSize: '14px',
                    outline: 'none',
                    transition: 'all 0.2s',
                    boxSizing: 'border-box'
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = '#000';
                    e.target.style.boxShadow = '0 0 0 2px rgba(0,0,0,0.1)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = '#d1d5db';
                    e.target.style.boxShadow = 'none';
                  }}
                />
              </div>

              {/* Username (Sign up only) */}
              {!isLogin && (
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: 500,
                    marginBottom: '8px'
                  }}>
                    Username
                  </label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="johndoe"
                    required
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      background: '#f9fafb',
                      border: '1px solid #d1d5db',
                      borderRadius: '8px',
                      fontSize: '14px',
                      outline: 'none',
                      transition: 'all 0.2s',
                      boxSizing: 'border-box'
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#000';
                      e.target.style.boxShadow = '0 0 0 2px rgba(0,0,0,0.1)';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = '#d1d5db';
                      e.target.style.boxShadow = 'none';
                    }}
                  />
                  <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                    This will be displayed in your profile
                  </p>
                </div>
              )}

              {/* Password */}
              <div>
                <label style={{
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: 500,
                  marginBottom: '8px'
                }}>
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  minLength={8}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    background: '#f9fafb',
                    border: '1px solid #d1d5db',
                    borderRadius: '8px',
                    fontSize: '14px',
                    outline: 'none',
                    transition: 'all 0.2s',
                    boxSizing: 'border-box'
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = '#000';
                    e.target.style.boxShadow = '0 0 0 2px rgba(0,0,0,0.1)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = '#d1d5db';
                    e.target.style.boxShadow = 'none';
                  }}
                />
                {!isLogin && (
                  <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '8px' }}>
                    <p style={{ margin: '0 0 4px 0', fontWeight: 500 }}>Password must include:</p>
                    <ul style={{ margin: 0, paddingLeft: '20px' }}>
                      <li>At least 8 characters</li>
                      <li>One uppercase letter (A-Z)</li>
                      <li>One lowercase letter (a-z)</li>
                      <li>One number (0-9)</li>
                      <li>One special character (!@#$%^&*)</li>
                    </ul>
                  </div>
                )}
              </div>

              {/* Confirm Password (Sign up only) */}
              {!isLogin && (
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: 500,
                    marginBottom: '8px'
                  }}>
                    Confirm password
                  </label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    minLength={8}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      background: '#f9fafb',
                      border: '1px solid #d1d5db',
                      borderRadius: '8px',
                      fontSize: '14px',
                      outline: 'none',
                      transition: 'all 0.2s',
                      boxSizing: 'border-box'
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#000';
                      e.target.style.boxShadow = '0 0 0 2px rgba(0,0,0,0.1)';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = '#d1d5db';
                      e.target.style.boxShadow = 'none';
                    }}
                  />
                </div>
              )}

              {/* Forgot Password Link (Login only) */}
              {isLogin && (
                <div style={{ textAlign: 'right' }}>
                  <button
                    type="button"
                    onClick={() => router.push('/forgot-password')}
                    style={{
                      fontSize: '14px',
                      color: '#6b7280',
                      border: 'none',
                      background: 'transparent',
                      cursor: 'pointer',
                      transition: 'color 0.2s'
                    }}
                    onMouseOver={(e) => e.currentTarget.style.color = '#000'}
                    onMouseOut={(e) => e.currentTarget.style.color = '#6b7280'}
                  >
                    Forgot password?
                  </button>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  background: isLoading ? '#d1d5db' : '#000',
                  color: 'white',
                  fontWeight: 500,
                  borderRadius: '8px',
                  border: 'none',
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                  transition: 'opacity 0.2s',
                  boxShadow: isLoading ? 'none' : '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                  opacity: isLoading ? 0.5 : 1
                }}
                onMouseOver={(e) => !isLoading && (e.currentTarget.style.opacity = '0.9')}
                onMouseOut={(e) => !isLoading && (e.currentTarget.style.opacity = '1')}
              >
                {isLoading ? (
                  <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                    <span style={{
                      display: 'inline-block',
                      width: '16px',
                      height: '16px',
                      border: '2px solid white',
                      borderTop: '2px solid transparent',
                      borderRadius: '50%',
                      animation: 'spin 1s linear infinite'
                    }} />
                    {isLogin ? 'Signing in...' : 'Creating account...'}
                  </span>
                ) : (
                  isLogin ? 'Sign in' : 'Create account'
                )}
              </button>
            </form>

            {/* Toggle Login/Signup */}
            <div style={{
              marginTop: '24px',
              textAlign: 'center',
              fontSize: '14px',
              color: '#6b7280'
            }}>
              {isLogin ? "Don't have an account?" : "Already have an account?"}{' '}
              <button
                onClick={() => {
                  const switchingToSignup = isLogin; // Currently on login, switching to signup
                  if (switchingToSignup && typeof window !== 'undefined') {
                    // CRITICAL: Clear token when switching to signup to prevent data leakage
                    localStorage.removeItem('token');
                  }
                  setIsLogin(!isLogin);
                  setError('');
                  setUsername('');
                  setPassword('');
                  setConfirmPassword('');
                }}
                style={{
                  color: '#000',
                  fontWeight: 500,
                  border: 'none',
                  background: 'transparent',
                  cursor: 'pointer',
                  textDecoration: 'none'
                }}
                onMouseOver={(e) => e.currentTarget.style.textDecoration = 'underline'}
                onMouseOut={(e) => e.currentTarget.style.textDecoration = 'none'}
              >
                {isLogin ? 'Sign up' : 'Sign in'}
              </button>
            </div>

            {/* Terms & Privacy */}
            {!isLogin && (
              <div style={{
                marginTop: '24px',
                textAlign: 'center',
                fontSize: '12px',
                color: '#9ca3af'
              }}>
                By creating an account, you agree to our{' '}
                <a
                  href="#"
                  style={{ textDecoration: 'underline', color: 'inherit' }}
                  onMouseOver={(e) => e.currentTarget.style.color = '#000'}
                  onMouseOut={(e) => e.currentTarget.style.color = '#9ca3af'}
                >
                  Terms of Service
                </a>
                {' '}and{' '}
                <a
                  href="#"
                  style={{ textDecoration: 'underline', color: 'inherit' }}
                  onMouseOver={(e) => e.currentTarget.style.color = '#000'}
                  onMouseOut={(e) => e.currentTarget.style.color = '#9ca3af'}
                >
                  Privacy Policy
                </a>
              </div>
            )}
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
