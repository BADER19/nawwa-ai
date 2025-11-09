import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { Check } from 'lucide-react';
import { api } from '../lib/api';

export default function PricingPage() {
  const router = useRouter();
  const [isYearly, setIsYearly] = useState(false);
  const [loading, setLoading] = useState<string | null>(null);

  const handleCheckout = async (tier: 'PRO' | 'TEAM', billing: 'monthly' | 'yearly') => {
    setLoading(`${tier}_${billing}`);

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/auth');
        return;
      }

      const response = await api.post('/subscription/create-checkout-session', {
        tier,
        billing,
        success_url: `${window.location.origin}/dashboard?session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${window.location.origin}/pricing`
      });

      // Redirect to PayPal Checkout
      window.location.href = response.data.url;
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to start checkout');
      setLoading(null);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(to bottom, #fcfcfc 0%, #f5f5f5 100%)',
      padding: '40px 20px'
    }}>
      {/* Header */}
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '60px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}
               onClick={() => router.push('/')}>
            <img src="/assets/logo/logo.svg" alt="logo" style={{ height: '80px', width: '80px' }} />
            <span style={{ fontSize: '20px', fontWeight: 600 }}>Nawwa</span>
          </div>
          <button
            onClick={() => router.push('/dashboard')}
            style={{
              padding: '10px 20px',
              background: 'transparent',
              color: '#000',
              border: '1px solid #e0e0e0',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 500
            }}
          >
            Back to Dashboard
          </button>
        </div>

        {/* Hero */}
        <div style={{ textAlign: 'center', marginBottom: '50px' }}>
          <h1 style={{ fontSize: '48px', fontWeight: 700, marginBottom: '16px' }}>
            Simple, transparent pricing
          </h1>
          <p style={{ fontSize: '20px', color: '#666', marginBottom: '40px' }}>
            Choose the plan that's right for you
          </p>

          {/* Billing Toggle */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '16px',
            padding: '6px',
            background: 'white',
            borderRadius: '10px',
            border: '1px solid #e0e0e0'
          }}>
            <button
              onClick={() => setIsYearly(false)}
              style={{
                padding: '10px 24px',
                background: !isYearly ? '#000' : 'transparent',
                color: !isYearly ? 'white' : '#666',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 600,
                transition: 'all 0.2s'
              }}
            >
              Monthly
            </button>
            <button
              onClick={() => setIsYearly(true)}
              style={{
                padding: '10px 24px',
                background: isYearly ? '#000' : 'transparent',
                color: isYearly ? 'white' : '#666',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 600,
                transition: 'all 0.2s',
                position: 'relative'
              }}
            >
              Yearly
              <span style={{
                position: 'absolute',
                top: '-8px',
                right: '-8px',
                background: '#4caf50',
                color: 'white',
                fontSize: '10px',
                padding: '2px 6px',
                borderRadius: '10px',
                fontWeight: 700
              }}>
                SAVE 16%
              </span>
            </button>
          </div>
        </div>

        {/* Pricing Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '30px',
          maxWidth: '1000px',
          margin: '0 auto'
        }}>
          {/* FREE Tier */}
          <div style={{
            background: 'white',
            border: '2px solid #e0e0e0',
            borderRadius: '16px',
            padding: '40px',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <div style={{ marginBottom: '24px' }}>
              <h3 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '8px' }}>FREE</h3>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginBottom: '16px' }}>
                <span style={{ fontSize: '48px', fontWeight: 700 }}>$0</span>
                <span style={{ color: '#666' }}>/month</span>
              </div>
              <p style={{ color: '#666', fontSize: '14px' }}>Perfect for trying out Nawwa</p>
            </div>

            <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 30px 0', flex: 1 }}>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Check size={16} strokeWidth={2} style={{ color: '#10b981', flexShrink: 0 }} /> 10 visualizations/month
              </li>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Check size={16} strokeWidth={2} style={{ color: '#10b981', flexShrink: 0 }} /> 3 workspaces
              </li>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Check size={16} strokeWidth={2} style={{ color: '#10b981', flexShrink: 0 }} /> Basic AI model (GPT-4o Mini)
              </li>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Check size={16} strokeWidth={2} style={{ color: '#10b981', flexShrink: 0 }} /> Basic shapes & charts
              </li>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center', opacity: 0.5 }}>
                <span style={{ width: '16px', height: '16px', border: '2px solid #ef4444', borderRadius: '50%', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', color: '#ef4444', fontWeight: 'bold' }}>✕</span> <span style={{ color: '#666' }}>No AI image generation</span>
              </li>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center', opacity: 0.5 }}>
                <span style={{ width: '16px', height: '16px', border: '2px solid #ef4444', borderRadius: '50%', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', color: '#ef4444', fontWeight: 'bold' }}>✕</span> <span style={{ color: '#666' }}>No voice input</span>
              </li>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Check size={16} strokeWidth={2} style={{ color: '#10b981', flexShrink: 0 }} /> Community support
              </li>
            </ul>

            <button
              onClick={() => router.push('/auth')}
              style={{
                width: '100%',
                padding: '14px',
                background: 'transparent',
                color: '#000',
                border: '2px solid #000',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Get Started
            </button>
          </div>

          {/* PRO Tier */}
          <div style={{
            background: 'white',
            border: '3px solid #667eea',
            borderRadius: '16px',
            padding: '40px',
            display: 'flex',
            flexDirection: 'column',
            position: 'relative',
            boxShadow: '0 10px 40px rgba(102, 126, 234, 0.2)'
          }}>
            <div style={{
              position: 'absolute',
              top: '-15px',
              left: '50%',
              transform: 'translateX(-50%)',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              padding: '6px 20px',
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: 700
            }}>
              MOST POPULAR
            </div>

            <div style={{ marginBottom: '24px' }}>
              <h3 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '8px' }}>PRO</h3>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginBottom: '16px' }}>
                <span style={{ fontSize: '48px', fontWeight: 700 }}>
                  ${isYearly ? '190' : '19'}
                </span>
                <span style={{ color: '#666' }}>/{isYearly ? 'year' : 'month'}</span>
              </div>
              <p style={{ color: '#666', fontSize: '14px' }}>For professionals & creators</p>
            </div>

            <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 30px 0', flex: 1 }}>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Check size={16} strokeWidth={2} style={{ color: '#10b981', flexShrink: 0 }} /> 500 visualizations/month
              </li>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Check size={16} strokeWidth={2} style={{ color: '#10b981', flexShrink: 0 }} /> Unlimited workspaces
              </li>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Check size={16} strokeWidth={2} style={{ color: '#10b981', flexShrink: 0 }} /> <strong>Advanced AI model (GPT-4o)</strong> - Smarter than Free
              </li>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Check size={16} strokeWidth={2} style={{ color: '#10b981', flexShrink: 0 }} /> <strong>🎤 Voice input enabled</strong>
              </li>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Check size={16} strokeWidth={2} style={{ color: '#10b981', flexShrink: 0 }} /> All visualization types
              </li>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Check size={16} strokeWidth={2} style={{ color: '#10b981', flexShrink: 0 }} /> Export to PNG/SVG
              </li>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Check size={16} strokeWidth={2} style={{ color: '#10b981', flexShrink: 0 }} /> Priority support
              </li>
            </ul>

            <button
              onClick={() => handleCheckout('PRO', isYearly ? 'yearly' : 'monthly')}
              disabled={loading === `PRO_${isYearly ? 'yearly' : 'monthly'}`}
              style={{
                width: '100%',
                padding: '14px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: 600,
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.7 : 1
              }}
            >
              {loading === `PRO_${isYearly ? 'yearly' : 'monthly'}` ? 'Loading...' : 'Upgrade to PRO'}
            </button>
          </div>

          {/* TEAM Tier */}
          <div style={{
            background: 'white',
            border: '2px solid #e0e0e0',
            borderRadius: '16px',
            padding: '40px',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <div style={{ marginBottom: '24px' }}>
              <h3 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '8px' }}>TEAM</h3>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginBottom: '16px' }}>
                <span style={{ fontSize: '48px', fontWeight: 700 }}>
                  ${isYearly ? '490' : '49'}
                </span>
                <span style={{ color: '#666' }}>/{isYearly ? 'year' : 'month'}</span>
              </div>
              <p style={{ color: '#666', fontSize: '14px' }}>For teams & businesses</p>
            </div>

            <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 30px 0', flex: 1 }}>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Check size={16} strokeWidth={2} style={{ color: '#10b981', flexShrink: 0 }} /> 2,500 visualizations/month
              </li>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Check size={16} strokeWidth={2} style={{ color: '#10b981', flexShrink: 0 }} /> 5 team members
              </li>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Check size={16} strokeWidth={2} style={{ color: '#10b981', flexShrink: 0 }} /> <strong>Advanced AI model (GPT-4o)</strong> - Smarter than Free
              </li>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Check size={16} strokeWidth={2} style={{ color: '#10b981', flexShrink: 0 }} /> <strong>🎤 Voice input enabled</strong>
              </li>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Check size={16} strokeWidth={2} style={{ color: '#10b981', flexShrink: 0 }} /> Team collaboration
              </li>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Check size={16} strokeWidth={2} style={{ color: '#10b981', flexShrink: 0 }} /> API access
              </li>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Check size={16} strokeWidth={2} style={{ color: '#10b981', flexShrink: 0 }} /> Custom branding
              </li>
              <li style={{ padding: '8px 0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Check size={16} strokeWidth={2} style={{ color: '#10b981', flexShrink: 0 }} /> Priority chat support
              </li>
            </ul>

            <button
              onClick={() => handleCheckout('TEAM', isYearly ? 'yearly' : 'monthly')}
              disabled={loading === `TEAM_${isYearly ? 'yearly' : 'monthly'}`}
              style={{
                width: '100%',
                padding: '14px',
                background: '#000',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: 600,
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.7 : 1
              }}
            >
              {loading === `TEAM_${isYearly ? 'yearly' : 'monthly'}` ? 'Loading...' : 'Upgrade to TEAM'}
            </button>
          </div>
        </div>

        {/* Enterprise */}
        <div style={{
          maxWidth: '800px',
          margin: '60px auto 0',
          padding: '40px',
          background: 'white',
          borderRadius: '16px',
          border: '2px solid #e0e0e0',
          textAlign: 'center'
        }}>
          <h3 style={{ fontSize: '28px', fontWeight: 600, marginBottom: '12px' }}>Enterprise</h3>
          <p style={{ fontSize: '16px', color: '#666', marginBottom: '24px' }}>
            Custom solutions for large organizations with unlimited visualizations, dedicated support, and on-premise options
          </p>
          <button
            onClick={() => window.location.href = 'mailto:sales@nawwa.ai'}
            style={{
              padding: '12px 32px',
              background: 'transparent',
              color: '#000',
              border: '2px solid #000',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Contact Sales
          </button>
        </div>

        {/* FAQ */}
        <div style={{ maxWidth: '800px', margin: '80px auto', textAlign: 'center' }}>
          <h3 style={{ fontSize: '32px', fontWeight: 600, marginBottom: '40px' }}>
            Frequently Asked Questions
          </h3>
          <div style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div>
              <h4 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>
                Can I change plans later?
              </h4>
              <p style={{ color: '#666' }}>
                Yes! You can upgrade or downgrade at any time. Changes take effect immediately.
              </p>
            </div>
            <div>
              <h4 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>
                What payment methods do you accept?
              </h4>
              <p style={{ color: '#666' }}>
                We accept all major credit cards and PayPal accounts. All payments are secure and encrypted through PayPal.
              </p>
            </div>
            <div>
              <h4 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>
                Can I cancel anytime?
              </h4>
              <p style={{ color: '#666' }}>
                Absolutely. Cancel anytime from your dashboard. No questions asked, no fees.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
